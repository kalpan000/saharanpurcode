(function() {
    "use strict";

    // custom scrollbar

    $("html").niceScroll({ styler: "fb", cursorcolor: "#68ae00", cursorwidth: '6', cursorborderradius: '10px', background: '#FFFFFF', spacebarenabled: false, cursorborder: '0', zindex: '1000' });

    $(".scrollbar1").niceScroll({ styler: "fb", cursorcolor: "#68ae00", cursorwidth: '6', cursorborderradius: '0', autohidemode: 'false', background: '#FFFFFF', spacebarenabled: false, cursorborder: '0' });



    $(".scrollbar1").getNiceScroll();
    if ($('body').hasClass('scrollbar1-collapsed')) {
        $(".scrollbar1").getNiceScroll().hide();
    }

})(jQuery);

function objectifyForm(formArray) {
    var returnArray = {};
    for (var i = 0; i < formArray.length; i++) {
        returnArray[formArray[i].name] = formArray[i].value;
    }
    return returnArray;
}

function makeDefaultTopolgy(type) {
    $.post("/topology/fav/", { "type": type }, function(data, status) {
        alert(data["msg"]);
    })
}

function ConvertSectoDay(n) {
    var day = parseInt(n / (24 * 3600));

    n = n % (24 * 3600);
    var hour = parseInt(n / 3600);

    n %= 3600;
    var minutes = n / 60;

    n %= 60;
    var seconds = n;

    return [day + " " + "Days ", hour + " " + "H : " + minutes.toFixed() + " " + "M : " + seconds.toFixed() + " " + "S"]
}

$(window).on('resize', function() {
    $("[_echarts_instance_]").each(function() {
        window.echarts.getInstanceById($(this).attr('_echarts_instance_')).resize()
    });
});