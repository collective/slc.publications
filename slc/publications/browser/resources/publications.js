(function () {
    "use strict";

    var MAX_RESULTS = 10,
        showAll = false;

    // fetch the publications based on provided search criteria and populate
    // the results table
    function queryPublications() {
        var query = $("#publicationsFilter").serialize(),
            resultsCount = 0;

        // helper function to toggle the display of 'Show all' and
        // 'Show only latest 10' links
        function toggleShowAll() {
            if (resultsCount < MAX_RESULTS) {
                $("#show-all").hide();
                $("#show-latest").hide();
            } else if (showAll) {
                $("#show-all").hide();
                $("#show-latest").show();
            } else {
                $("#show-all").show();
                $("#show-latest").hide();
            }
        }

        // helper function to show the results table or a suitable message
        // if no results have been found
        function showResults() {
            if (resultsCount > 0) {
                $("#resultTable").show();
                $("#noResults").hide();
            } else {
                $("#resultTable").hide();
                $("#noResults").show();
            }
            // hide featured publications
            $("#highlightsContainer").hide();
            $("#show-highlights").show();

            // change results header
            $("#publication-results-heading-latest").hide();
            $("#publication-results-heading").hide();
        }

        // show "Loading..." message
        $('#loading').show();

        $.getJSON(
            "publications_view.json?" + query,
            function (data) {
                var items = [],
                    results = "";

                $.each(data, function (key, val) {
                    var link = "<a href='" + val.path + "'>" + val.title + "</a>";
                    items.push('<tr><td>' + link + '</td><td>' +
                               val.year + '</td><td>' +
                               val.type_title + '</td><td><em class="discrete size">' +
                               val.size + '</em></td></tr>');
                });

                results = $('<tbody/>', {html: items.join('')});
                resultsCount = items.length;
                $("#resultTable tbody").replaceWith(results);

                showResults();
                toggleShowAll();

                // hide "Loading..." message
                $('#loading').hide();
            }
        );
    }

    $(document).ready(function () {

        $("#publicationsFilter :input").change(function () {
            queryPublications();
        });

        $("#show-all").click(function () {
            $("#publicationsFilter").append("<input type='hidden' name='show-all' value='True'/>");
            showAll = true;
            queryPublications();
            return false;
        });

        $("#show-latest").click(function () {
            $("input[name='show-all']").remove();
            showAll = false;
            queryPublications();
            return false;
        });

        $("#show-highlights a").click(function () {
            $("#highlightsContainer").show();
            $("#show-highlights").hide();
            return false;
        });

        var timeout;
        $("input[name=SearchableText]").keyup(function () {
            window.clearTimeout(timeout);
            timeout = window.setTimeout(function () {
                queryPublications();
            }, 350);
        });

        // show tooltips
        $('a.tooltip').each(function () {
            var helptext = $($(this).attr('rel'));

            $(this).qtip({
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
        $("#queryPublications").unbind('click');

        var recentcarousel = $(".recentcarousel").jcarousel({scroll: 1});
    });

}());
