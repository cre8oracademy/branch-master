from django import template
 
register = template.Library()
 
LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 2 
ADJACENT_PAGES = 4
# code from http://blog.localkinegrinds.com/2007/09/06/digg-style-pagination-in-django/
# adapted to use django.core.paginator instance.

def digg_paginator(context):
    context["is_paginated"] = context["paginator"].per_page < context["paginator"].count
    if (context["is_paginated"]):
        " Initialize variables "
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
       
        if (context["paginator"].num_pages <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, context["paginator"].num_pages + 1) if n > 0 and n <= context["paginator"].num_pages]           
        elif (context["posts"].number <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= context["paginator"].num_pages]
            pages_outside_leading_range = [n + context["paginator"].num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (context["posts"].number > context["paginator"].num_pages - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_numbers = [n for n in range(context["paginator"].num_pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, context["paginator"].num_pages + 1) if n > 0 and n <= context["paginator"].num_pages]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else: 
            page_numbers = [n for n in range(context["posts"].number - ADJACENT_PAGES, context["posts"].number + ADJACENT_PAGES + 1) if n > 0 and n <= context["paginator"].num_pages]
            pages_outside_leading_range = [n + context["paginator"].num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        return {
            "base_url": context["base_url"],
            "is_paginated": context["is_paginated"],
            "previous": context["posts"].previous_page_number(),
            "has_previous": context["posts"].has_previous(),
            "next": context["posts"].next_page_number(),
            "has_next": context["posts"].has_next(),
            "page": context["posts"].number,
            "pages": context["paginator"].num_pages,
            "page_numbers": page_numbers,
            "in_leading_range" : in_leading_range,
            "in_trailing_range" : in_trailing_range,
            "pages_outside_leading_range": pages_outside_leading_range,
            "pages_outside_trailing_range": pages_outside_trailing_range
        }
 
register.inclusion_tag("snapboard/include/digg_paginator.html", takes_context=True)(digg_paginator)