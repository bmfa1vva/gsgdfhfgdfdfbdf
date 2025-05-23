# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Brand, Color, Condition, Size
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import HeaderBanner
from django.db.models import Q, F

def product_list(request):
    products_list = Product.objects.all().select_related('brand', 'category').prefetch_related('colors', 'sizes', 'images')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()
    conditions = Condition.objects.all()
    sizes = Size.objects.all()

    category_slug = request.GET.get('category')
    brand_name = request.GET.get('brand')
    color_name = request.GET.get('color')
    condition_name = request.GET.get('condition')
    size_name = request.GET.get('size')
    gender = request.GET.get('gender')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    # --- НОВОЕ: ПОИСКОВЫЙ ЗАПРОС ---
    search_query = request.GET.get('search_query')
    # --- КОНЕЦ НОВОГО ---

    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    if brand_name:
        products_list = products_list.filter(brand__name=brand_name)
    if color_name:
        products_list = products_list.filter(colors__name=color_name).distinct()
    if condition_name:
        products_list = products_list.filter(condition__name=condition_name)
    if size_name:
        products_list = products_list.filter(sizes__name=size_name).distinct()
    if gender:
        products_list = products_list.filter(gender=gender)

    # --- НОВОЕ: ФИЛЬТРАЦИЯ ПО ПОИСКОВОМУ ЗАПРОСУ ---
    if search_query:
        # Используем Q-объекты для OR-условий, если нужно искать по нескольким полям
        # Сейчас ищем только по search_keywords
        products_list = products_list.filter(
            Q(search_keywords__icontains=search_query) # icontains - нечувствительный к регистру поиск подстроки
            # Можно добавить другие поля для поиска, например:
            # | Q(name__icontains=search_query)
            # | Q(description__icontains=search_query)
        )
    # --- КОНЕЦ НОВОГО ---

    # Фильтрация по цене (с учётом скидок)
    if price_min or price_max:
        price_filters = Q()
        if price_min:
            price_min = float(price_min)
            price_filters &= (
                Q(discount_price__isnull=False, discount_price__gte=price_min) |
                Q(discount_price__isnull=True, price__gte=price_min)
            )
        if price_max:
            price_max = float(price_max)
            price_filters &= (
                Q(discount_price__isnull=False, discount_price__lte=price_max) |
                Q(discount_price__isnull=True, price__lte=price_max)
            )
        products_list = products_list.filter(price_filters)

    paginator = Paginator(products_list, 10)
    page = request.GET.get('page')
    try:
        products = paginator.get_page(page)
    except PageNotAnInteger:
        products = paginator.get_page(1)
    except EmptyPage:
        products = paginator.get_page(paginator.num_pages)

    cart_count = request.session.get('cart', {}).get('count', 0)

    # ⬇️ ДОБАВЛЯЕМ БАННЕР
    banner = HeaderBanner.objects.filter(is_active=True, show_on_homepage=True).first()

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'colors': colors,
        'conditions': conditions,
        'sizes': sizes,
        'category': get_object_or_404(Category, slug=category_slug) if category_slug else None,
        'selected_brand': brand_name,
        'selected_color': color_name,
        'selected_condition': condition_name,
        'selected_size': size_name,
        'selected_gender': gender,
        'price_min': price_min,
        'price_max': price_max,
        'search_query': search_query, # --- НОВОЕ: Передаем поисковый запрос в шаблон
        'cart_count': cart_count,
        'banner': banner,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        cart = request.session.get('cart', {'items': {}})
        product_id = str(product.id)
        price = float(product.discount_price or product.price)
        if product_id in cart['items']:
            cart['items'][product_id]['quantity'] += 1
        else:
            cart['items'][product_id] = {
                'product_id': product.id,
                'name': product.name,
                'price': price,
                'quantity': 1
            }
        cart['count'] = sum(item['quantity'] for item in cart['items'].values())
        request.session['cart'] = cart

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"{product.name} добавлен в корзину!",
                'cart_count': cart['count']
            })

        messages.success(request, f"{product.name} добавлен в корзину!")
        return redirect('store:product_list')

    cart_count = request.session.get('cart', {}).get('count', 0)
    return render(request, 'product_detail.html', {'product': product, 'cart_count': cart_count})


def get_filtered_options(request):
    """
    Возвращает JSON с отфильтрованными опциями (размеры, категории и т.д.)
    на основе текущих выбранных фильтров.
    """
    selected_category_slug = request.GET.get('category')
    selected_brand_name = request.GET.get('brand')
    selected_color_name = request.GET.get('color')
    selected_condition_name = request.GET.get('condition')
    selected_size_name = request.GET.get('size')
    selected_gender = request.GET.get('gender')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    # --- НОВОЕ: ПОИСКОВЫЙ ЗАПРОС для фильтрации опций ---
    search_query = request.GET.get('search_query')
    # --- КОНЕЦ НОВОГО ---

    # Исходный queryset для фильтрации опций
    # Начинаем с всех продуктов и затем применяем фильтры
    products_for_options = Product.objects.all()

    if selected_category_slug:
        products_for_options = products_for_options.filter(category__slug=selected_category_slug)
    if selected_brand_name:
        products_for_options = products_for_options.filter(brand__name=selected_brand_name)
    if selected_color_name:
        products_for_options = products_for_options.filter(colors__name=selected_color_name)
    if selected_condition_name:
        products_for_options = products_for_options.filter(condition__name=selected_condition_name)
    if selected_size_name:
        products_for_options = products_for_options.filter(sizes__name=selected_size_name)
    if selected_gender:
        products_for_options = products_for_options.filter(gender=selected_gender)

    # --- НОВОЕ: ФИЛЬТРАЦИЯ ОПЦИЙ ПО ПОИСКОВОМУ ЗАПРОСУ ---
    if search_query:
        products_for_options = products_for_options.filter(
            Q(search_keywords__icontains=search_query)
        )
    # --- КОНЕЦ НОВОГО ---

    # Фильтрация по цене для корректного отображения опций
    if price_min or price_max:
        price_filters = Q()
        if price_min:
            price_min = float(price_min)
            price_filters &= (
                    Q(discount_price__isnull=False, discount_price__gte=price_min) |
                    Q(discount_price__isnull=True, price__gte=price_min)
            )
        if price_max:
            price_max = float(price_max)
            price_filters &= (
                    Q(discount_price__isnull=False, discount_price__lte=price_max) |
                    Q(discount_price__isnull=True, price__lte=price_max)
            )
        products_for_options = products_for_options.filter(price_filters)

    # Собираем уникальные опции на основе отфильтрованных продуктов
    # Важно использовать .distinct() для избежания дубликатов
    available_categories = list(
        Category.objects.filter(
            products__in=products_for_options
        ).distinct().values('slug', 'name')
    )
    available_brands = list(
        Brand.objects.filter(
            product__in=products_for_options
        ).distinct().values('name')
    )
    available_colors = list(
        Color.objects.filter(
            product__in=products_for_options
        ).distinct().values('name')
    )
    available_conditions = list(
        Condition.objects.filter(
            product__in=products_for_options
        ).distinct().values('name')
    )
    available_sizes = list(
        Size.objects.filter(
            product__in=products_for_options
        ).distinct().values('name')
    )

    # Пол - это просто список возможных значений, он не меняется динамически
    # в зависимости от выбора других фильтров, но мы можем его отправить для согласованности
    available_genders = [
        {'value': choice[0], 'name': choice[1]} for choice in Product.GENDER_CHOICES
    ]

    data = {
        'categories': available_categories,
        'brands': available_brands,
        'colors': available_colors,
        'conditions': available_conditions,
        'sizes': available_sizes,
        'genders': available_genders,
    }
    return JsonResponse(data)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    cart_count = request.session.get('cart', {}).get('count', 0)
    return render(request, 'product_list.html', {
        'products': products,
        'categories': Category.objects.all(),
        'category': category,
        'cart_count': cart_count,
    })


def cart_view(request):
    cart = request.session.get('cart', {'items': {}})
    items = cart.get('items', {})
    cart_items_with_total = []
    for item_id, item in items.items():
        product = get_object_or_404(Product, id=item['product_id'])
        item_total = item['price'] * item['quantity']
        cart_items_with_total.append({
            'id': item_id,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total': item_total,
            'product': product
        })
    total = sum(item['price'] * item['quantity'] for item in items.values())
    cart_count = cart.get('count', 0)

    if request.method == 'POST' and 'remove_item' in request.POST:
        item_id = request.POST.get('item_id')
        if item_id in cart['items']:
            del cart['items'][item_id]
            cart['count'] = sum(item['quantity'] for item in cart['items'].values())
            request.session['cart'] = cart
            return redirect('store:cart')

    return render(request, 'cart.html', {
        'cart_items': cart_items_with_total,
        'total': total,
        'cart_count': cart_count
    })


def checkout_view(request):
    cart = request.session.get('cart', {'items': {}})
    items = cart.get('items', {})
    skus = []

    for item_id, item in items.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            skus.append(product.sku)
        except Product.DoesNotExist:
            continue

    skus_text = ", ".join(skus)
    message = f"Здравствуйте, меня интересуют товары с артикулами: {skus_text}."
    countdown_time = 10  # Установите желаемое время ожидания в секундах

    return render(request, 'checkout.html', {
        'message': message,
        'has_items': len(skus) > 0,
        'countdown_time': countdown_time,  # Передаем время ожидания в контекст
    })

def home(request):
    banner = HeaderBanner.objects.filter(is_active=True, show_on_homepage=True).first()
    return render(request, 'store/home.html', {'banner': banner})