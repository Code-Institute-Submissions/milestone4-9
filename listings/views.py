from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Listing, Category
from .forms import ListingForm

# Create your views here.

def all_listings(request):
    """ A view to show all listings, including sorting and search queries """

    listings = Listing.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                listings = listings.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            listings = listings.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            listings = listings.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('listings'))
            
            queries = Q(name__icontains=query) | Q(about__icontains=query)
            listings = listings.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'listings': listings,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'listings/listings.html', context)


def listing_detail(request, listing_id):
    """ A view to show individual listing details """

    listing = get_object_or_404(Listing, pk=listing_id)

    context = {
        'listing': listing,
    }

    return render(request, 'listings/listing_detail.html', context)


def add_listing(request):
    """ Add a listing to the store """
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save()
            messages.success(request, 'Successfully added listing!')
            return redirect(reverse('listing_detail', args=[listing.id]))
        else:
            messages.error(request, 'Failed to add listing. Please ensure the form is valid.')
    else:
        form = ListingForm()
        
    template = 'listings/add_listing.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


def edit_listing(request, listing_id):
    """ Edit a listing in the store """
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated listing!')
            return redirect(reverse('listing_detail', args=[listing.id]))
        else:
            messages.error(request, 'Failed to update listing. Please ensure the form is valid.')
    else:
        form = ListingForm(instance=listing)
        messages.info(request, f'You are editing {listing.name}')

    template = 'listings/edit_listing.html'
    context = {
        'form': form,
        'listing': listing,
    }

    return render(request, template, context)


def delete_listing(request, listing_id):
    """ Delete a listing from the store """
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.delete()
    messages.success(request, 'Listing deleted!')
    return redirect(reverse('listings'))