(function () {
    "use strict";

    var MAX_RESULTS = 10,
        showAll = false;

    // fetch the publications based on provided search criteria and populate
    // the results table
    function queryPublications() {
        var query = jQuery("#publicationsFilter").serialize(),
            resultsCount = 0;

        // helper function to toggle the display of 'Show all' and
        // 'Show only latest 10' links
        function toggleShowAll() {
            if (resultsCount < MAX_RESULTS) {
                jQuery("#show-all").hide();
                jQuery("#show-latest").hide();
            } else if (showAll) {
                jQuery("#show-all").hide();
                jQuery("#show-latest").show();
            } else {
                jQuery("#show-all").show();
                jQuery("#show-latest").hide();
            }
        }

        // helper function to show the results table or a suitable message
        // if no results have been found
        function showResults() {
            if (resultsCount > 0) {
                jQuery("#resultTable").show();
                jQuery("#noResults").hide();
            } else {
                jQuery("#resultTable").hide();
                jQuery("#noResults").show();
            }
            // hide featured publications
            jQuery("#highlightsContainer").hide();
            jQuery("#show-highlights").show();

            // change results header
            jQuery("#publication-results-heading-latest").hide();
            jQuery("#publication-results-heading").hide();
        }

        // show "Loading..." message
        jQuery('#loading').show();

        jQuery.getJSON(
            "publications_view.json?" + query,
            function (data) {
                var items = [],
                    results = "";

                jQuery.each(data, function (key, val) {
                    var link = "<a href='" + val.path + "'>" + val.title + "</a>";
                    items.push('<tr><td>' + link + '</td><td>' +
                               val.year + '</td><td>' +
                               val.type_title + '</td><td><em class="discrete size">' +
                               val.size + '</em></td></tr>');
                });

                results = jQuery('<tbody/>', {html: items.join('')});
                resultsCount = items.length;
                jQuery("#resultTable tbody").replaceWith(results);

                showResults();
                toggleShowAll();

                // hide "Loading..." message
                jQuery('#loading').hide();
            }
        );
    }

    jQuery(document).ready(function () {

        jQuery("#publicationsFilter :input").change(function () {
            queryPublications();
        });

        jQuery("#show-all").click(function () {
            jQuery("#publicationsFilter").append("<input type='hidden' name='show-all' value='True'/>");
            showAll = true;
            queryPublications();
            return false;
        });

        jQuery("#show-latest").click(function () {
            jQuery("input[name='show-all']").remove();
            showAll = false;
            queryPublications();
            return false;
        });

        jQuery("#show-highlights a").click(function () {
            jQuery("#highlightsContainer").show();
            jQuery("#show-highlights").hide();
            return false;
        });

        var timeout;
        jQuery("input[name=SearchableText]").keyup(function () {
            window.clearTimeout(timeout);
            timeout = window.setTimeout(function () {
                queryPublications();
            }, 350);
        });

        // show tooltips
        jQuery('a.tooltip').each(function () {
            var helptext = jQuery(jQuery(this).attr('rel'));

            jQuery(this).qtip({
                content: {
                    text: helptext,
                    title: {
                        text: '',
                        button: '<img onclick="return false;" src="pb_close.png" alt="Close" />'
                    }
                },
                position: {
                    corner: {
                        target: 'leftBottom',
                        tooltip: 'rightTop'
                    },
                    adjust: { x: -15, y: -50 }
                },
                show: { when: { event: 'click' } },
                hide: { when: { event: 'unfocus' } },
                style: {
                    //tip: { corner: 'rightMiddle' },
                    width: 625
                }
            });

        });

        // Don't warn the user that they have already submitted the form
        jQuery("#queryPublications").unbind('click');

        // initialize recent items carousel
        jQuery(".recentcarousel").jcarousel({scroll: 1});
    });

}());
