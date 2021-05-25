/* common javascript functions. */

/* Handle CSRF protection for AJAX requests
   See https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
   */

$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
// jQuery plugin to prevent double submission of forms from http://stackoverflow.com/a/4473801
jQuery.fn.preventDoubleSubmission = function() {
  $(this).bind('submit',function(e){
    var $form = $(this);

    if ($form.data('submitted') === true) {
      // Previously submitted - don't submit again
      e.preventDefault();
    } else {
      // Mark it so that the next submit can be ignored
      $form.data('submitted', true);
    }

   // Keep chainability
    return $form;
  });
};

// DFP ad code


// var googletag = googletag || {};
// googletag.cmd = googletag.cmd || [];
// (function() {
// var gads = document.createElement('script');
// gads.async = true;
// gads.type = 'text/javascript';
// var useSSL = 'https:' == document.location.protocol;
// gads.src = (useSSL ? 'https:' : 'http:') +
// '//www.googletagservices.com/tag/js/gpt.js';
// var node = document.getElementsByTagName('script')[0];
// node.parentNode.insertBefore(gads, node);
// })();


// googletag.cmd.push(function() {
// googletag.defineSlot('/5062006/Bottom_MPU', [300, 250], 'div-gpt-ad-1370613670378-0').addService(googletag.pubads());
// googletag.pubads().enableSingleRequest();
// googletag.enableServices();
// });
//
// googletag.cmd.push(function() {
// googletag.defineSlot('/5062006/MPU', [300, 250], 'div-gpt-ad-1370613897135-0').addService(googletag.pubads());
// googletag.pubads().enableSingleRequest();
// googletag.enableServices();
// });
//
// googletag.cmd.push(function() {
// googletag.defineSlot('/5062006/leaderboard', [728, 90], 'div-gpt-ad-1370613947355-0').addService(googletag.pubads());
// googletag.pubads().enableSingleRequest();
// googletag.enableServices();
// });
//
// googletag.cmd.push(function() {
// googletag.defineSlot('/5062006/Homepage_bigMPU', [336, 280], 'div-gpt-ad-1371162024909-0').addService(googletag.pubads());
// googletag.pubads().enableSingleRequest();
// googletag.enableServices();
// });
//
//
// googletag.cmd.push(function() {
// googletag.defineSlot('/5062006/big_bottom_mpu', [300, 600], 'div-gpt-ad-1380805535860-0').addService(googletag.pubads());
// googletag.pubads().enableSingleRequest();
// googletag.enableServices();
// });
// sidebar tabs
$(function () {
    var tabContainers = $('div.tabs > div');
    tabContainers.hide().filter(':first').show();

    $('div.tabs ul.tabNavigation a').click(function () {
        tabContainers.hide();
        tabContainers.filter(this.hash).show();
        $('div.tabs ul.tabNavigation a').removeClass('selected');
        $(this).addClass('selected');
        return false;
    }).filter(':first').click();

});

// rotate header banners

var banners = ['blur.jpg', 'girl_face.jpg', 'rocknroll.jpg', 'zip_darker.jpg'];

$(function() {
    im = "/static/bank/headers/"+banners[Math.floor(Math.random()*banners.length)];
    cs = 'url("'+im+'")';
    $('#header').css("background-image", cs);
});

// Stuart changes for menu
$(function() {
  $('#hamburger').click(function() {
    $('#navbar').show();
    $('.adsbygoogle').hide();
    $("body").addClass("modal-open");
  })
  $('#close').click(function() {
    $('#navbar').hide();
    $('.adsbygoogle').show();
    $("body").removeClass("modal-open");
  })
});
