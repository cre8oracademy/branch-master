/*
 * Plugin jQuery.BBCode
 * Version 0.2 
 *
 * Based on jQuery.BBCode plugin (http://www.kamaikinproject.ru)
 */
(function($){
  $.fn.bbcode = function(options){
		// default settings
    var options = $.extend({
      tag_bold: true,
      tag_italic: true,
      tag_underline: true,
      tag_link: false,
      tag_image: false,
      tag_smily: true,
      button_image: true,
      image_url: '/static/bank/icons/'
    },options||{});
    //  panel 
    var text = '<div id="bbcode_bb_bar">'
    if(options.tag_bold){
      text = text + '<a href="#" id="b" title="" class="bbbutton">';
      if(options.button_image){
        text = text + '<img src="' + options.image_url + 'text_bold.png" />';
      }else{
        text = text + 'Bold';
      }
      text = text + '</a>';
    }
    if(options.tag_italic){
      text = text + '<a href="#" id="i" title="" class="bbbutton">';
      if(options.button_image){
        text = text + '<img src="' + options.image_url + 'text_italic.png" />';
      }else{
        text = text + 'Italic';
      }
      text = text + '</a>';
    }
    if(options.tag_underline){
      text = text + '<a href="#" id="u" title="" class="bbbutton">';
      if(options.button_image){
        text = text + '<img src="' + options.image_url + 'text_underline.png" />';
      }else{
        text = text + 'Underscore';
      }
      text = text + '</a>';
    }
    if(options.tag_link){
      text = text + '<a href="#" id="url" title="" class="bbbutton">';
      if(options.button_image){
        text = text + '<img src="' + options.image_url + 'link.png" />';
      }else{
        text = text + 'Link';
      }
      text = text + '</a>';
    }
    if(options.tag_image){
      text = text + '<a href="#" id="img" title="" class="bbbutton">';
      if(options.button_image){
        text = text + '<img src="' + options.image_url + 'image.png" />';
      }else{
        text = text + 'Image';
      }
      text = text + '</a>';
    }
    // the list of available smileys is attached as a data object to the text
    // area that we are acting on. It's an array of objects with attributes
    // img, alt and title.
    if(options.tag_smily && $(this).data('smileys')) {
      smileys = $(this).data('smileys');
      text=text+'<a href="#" id="smile" title="" class="bbbutton"><img src="' + options.image_url + 'emoticon_smile.png" /></a>';
      text=text+'<div id="smileybar">';
      for (var i=0; i< smileys.length;i++) {
         text=text+'<a href="#" title="'+smileys[i].alt+'"><img src="'+smileys[i].img+'" alt="'+smileys[i].alt+'" title="'+smileys[i].title+'"></a>'
      }
      text=text+'</div>'
    }
    
    
    text = text + '</div>';
    
    $(this).wrap('<div id="bbcode_container"></div>');
    $("#bbcode_container").prepend(text);
    // $("#bbcode_bb_bar a img").css("border", "none");
    var id = '#' + $(this).attr("id");
    var e = $(id).get(0);
    
    $('#bbcode_bb_bar a.bbbutton').click(function() {
      var button_id = $(this).attr("id");
      if(button_id=='smile') {
        if ($('#smileybar').css('display')=='block') {
          $('#smileybar').css('display', 'none');
          return false;
        }
        // should this be done as a class? Display toggle wasn't working with all the extra attrs.
        $('#smileybar').css({'display': 'block', 'width': '150px', 'position': 'absolute', 'top': '-35px', 'left': '180px'});
        return false;
      }
      var start = '['+button_id+']';
      var end = '[/'+button_id+']';

	  var param="";
	  if (button_id=='smile') {
	    
	  }
	  if (button_id=='img')
	  {
	     param=prompt("Enter image URL","http://");
		 if (param)
			start+=param;
		 }
	  else if (button_id=='url')
	  {
			param=prompt("Enter URL","http://");
			if (param) 
				start = '[url=' + param + ']';
		 }
      insert(start, end, e);
      return false;
    });
    
    $('#smileybar a').click(function() {
       var sm = $(this).attr('title');
       var start=sm+' ';
       var end='';
       insert(start, end, e);
       return false;
  	})

    
	}
	  function insert(start, end, element) {
    if (document.selection) {
       element.focus();
       sel = document.selection.createRange();
       sel.text = start + sel.text + end;
    } else if (element.selectionStart || element.selectionStart == '0') {
       element.focus();
       var startPos = element.selectionStart;
       var endPos = element.selectionEnd;
       element.value = element.value.substring(0, startPos) + start + element.value.substring(startPos, endPos) + end + element.value.substring(endPos, element.value.length);
    } else {
      element.value += start + end;
    }
  }
 

  
})(jQuery);