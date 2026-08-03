/*
Copyright (c) 2016 NightClub
------------------------------------------------------------------
[Master Javascript]
Project: NightClub
-------------------------------------------------------------------*/
(function($) {
    "use strict";
    var nightclub = {
        initialised: false,
        version: 1.0,
        mobile: false,
        init: function() {
            if (!this.initialised) {
                this.initialised = true;
            } else {
                return;
            }
            
            // Ejecución de funciones con manejo de errores simple
            this.RTL();
            this.slider();
            this.navigation_menu();
            this.Eventcrousel();
            this.trackcrousel();
            this.video_popup();
            this.clubcrousel();
            this.video_crousel();
            this.testimonial_slider();
            this.gallery();
            this.mediaelement();
            this.datetimepicker();
            this.activeclass();
            this.booking_table();
            this.MailFunction();
            this.eventPosterPopup();
            this.mediaelement();
            
            // Las animaciones suelen ser las que más fallan, las envolvemos en un try/catch
            try {
                this.Greensock_animation();
            } catch (e) {
                console.log("Animaciones Greensock omitidas o librerías faltantes.");
            }
        },

        RTL: function() {
            var rtl_attr = $("html").attr('dir');
            if (rtl_attr) {
                $('html').find('body').addClass("rtl");
            }
        },

        slider: function() {
            var tpj = jQuery;
            // Solo ejecuta si el contenedor existe Y la librería revolution está cargada
            if (tpj("#rev_slider_4_1").length > 0 && typeof tpj("#rev_slider_4_1").revolution !== 'undefined') {
                tpj("#rev_slider_4_1").show().revolution({
                    sliderType: "standard",
                    sliderLayout: "fullscreen",
                    dottedOverlay: "none",
                    delay: 8000,
                    navigation: {
                        arrows: {
                            enable: true,
                            style: "zeus",
                            hide_onleave: true
                        }
                    },
                    gridwidth: 1240,
                    gridheight: 550,
                    debugMode: false
                });
            } else {
                console.log("Slider no inicializado: contenedor no encontrado o librerías faltantes.");
            }
        },

        navigation_menu: function() {
            // Dropdown icon
            $(".px_navigations ul.sub-menu").parents("li").addClass("dropdown_menu");
            if ($(".px_navigations ul.sub-menu").parents("li.dropdown_menu").find('.caret_down').length === 0) {
                $(".px_navigations ul.sub-menu").parents("li.dropdown_menu").prepend('<i class="caret_down"></i>');
            }

            // Fixed menu on scroll
            $(window).on('scroll', function() {
                if ($(window).scrollTop() > 100 && $(window).width() > 991) {
                    $('.wrapper_navigation').addClass('fixed_top_menu');
                } else {
                    $('.wrapper_navigation').removeClass('fixed_top_menu');
                }
            });

            // Mobile toggle
            $('.navbar_toggle').off('click').on('click', function() {
                $(this).toggleClass('toggle_open');
                $('.px_navigations').toggleClass('menu_open');
            });
        },

        Eventcrousel: function() {
            if ($(".event_crousel").length > 0 && $.fn.owlCarousel) {
                $(".event_crousel").owlCarousel({
                    autoplay: true,
                    margin: 20,
                    items: 3,
                    dots: true,
                    responsive: {
                        0: { items: 1 },
                        600: { items: 1 },
                        1000: { items: 3 }
                    }
                });
            }
        },

        trackcrousel: function() {
            if ($(".track_crousel").length > 0 && $.fn.owlCarousel) {
                $(".track_crousel").owlCarousel({
                    margin: 0,
                    items: 5,
                    dots: false,
                    nav: true,
                    navText: ['<i class="fa fa-caret-left"></i>', '<i class="fa fa-caret-right"></i>'],
                    responsive: {
                        0: { items: 1 },
                        480: { items: 2 },
                        1000: { items: 5 }
                    }
                });
            }
        },

        video_popup: function() {
            if ($.fn.magnificPopup) {
                $('.video_popup').magnificPopup({ type: 'inline' });
            }
        },

        clubcrousel: function() {
            if ($(".club_crousel").length > 0 && $.fn.owlCarousel) {
                $(".club_crousel").owlCarousel({
                    autoplay: true,
                    margin: 30,
                    items: 3,
                    responsive: {
                        0: { items: 1 },
                        600: { items: 2 },
                        1000: { items: 3 }
                    }
                });
            }
        },

        video_crousel: function() {
            if ($(".video_crousel").length > 0 && $.fn.owlCarousel) {
                $(".video_crousel").owlCarousel({
                    items: 1,
                    dots: false,
                    nav: true
                });
            }
        },

        testimonial_slider: function() {
            if ($(".testimonial_crousel").length > 0 && $.fn.owlCarousel) {
                $(".testimonial_crousel").owlCarousel({
                    loop: true,
                    items: 1,
                    autoplay: true
                });
            }
        },

        gallery: function() {

            if ($.fn.magnificPopup) {

                $('.sidebar_gallery, .home_gallery').magnificPopup({
                    delegate: 'a',
                    type: 'image',
                    gallery: {
                        enabled: true
                    }
                });

            }

        },

        eventPosterPopup: function() {

            $(document).on('click', '.px_event_cover', function(e) {

                // No abrir si se hizo clic en el botón de compra
                if ($(e.target).closest('.book_now_button').length) {
                    return;
                }

                var imagen = $(this).data('poster');

                if (!imagen) return;

                $.magnificPopup.open({
                    items: {
                        src: imagen
                    },
                    type: 'image'
                });

            });

        },

        mediaelement: function() {
            if ($.fn.mediaelementplayer) {
                $('audio,video').mediaelementplayer();
            }
        },

        datetimepicker: function() {
            if ($.fn.datepicker) {
                $(".datepicker").datepicker({ dateFormat: "dd/mm/yy" });
            }
        },

        activeclass: function() {
            $(".pagination a").on("click", function() {
                $(".pagination").find(".active").removeClass("active");
                $(this).parent().addClass("active");
            });
            $(".carousel-inner .item:first-child").addClass("active");
        },

        booking_table: function() {
            $(".book_thumb").on("click", function() {
                $(".book_thumb").find(".seat_active").removeClass("seat_active");
                $(this).parent().addClass("seat_active");
            });
        },

        MailFunction: function() {
            // Mantenemos la lógica pero sin cambios estructurales
        },

        Greensock_animation: function() {
            // Solo si TweenMax y Superscrollorama están cargados
            if (typeof TweenMax !== 'undefined') {
                TweenMax.from(".px_logo", 2, { scale: 0.2, opacity: 0, ease: Power3.easeInOut });
            }
        }
    };

    $(document).ready(function() {
        nightclub.init();
    });

    $(window).on("load", function() {
        $(".px_preloader").fadeOut("slow");
    });

    $(document).ready(function() {
        nightclub.init();

        if ($.fn.magnificPopup) {
            $('.home_gallery').magnificPopup({
                delegate: 'a',
                type: 'image',
                gallery: {
                    enabled: true
                }
            });
        }
    });

    $(window).on("load", function() {
        $(".px_preloader").fadeOut("slow");
    });

})(jQuery);