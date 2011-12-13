var PUBS = {};

PUBS.queryPublications = function () {
    var query = jQuery("#publicationsFilter").serialize();
    jQuery.getJSON(
        "publications_view.json?" + query, function (data) {
            var items = [],
            results = "";
            jQuery.each(data, function (key, val) {
                var link = "<a href='" + val.path + "'>" + val.title + "</a>";
                items.push('<tr><td>' + link + '</td><td>' +
                           val.effective_date + '</td><td>' +
                           val.type + '</td><td><em class="discrete size">' +
                           val.size + '</em></td></tr>');
            });
            results = jQuery('<tbody/>', {html: items.join('')});
            jQuery("#resultTable tbody").replaceWith(results);
        });
};

jQuery(document).ready(function() {
    jQuery("#publicationsFilter :input").change(function () {
        PUBS.queryPublications();
        return false;
    });
    jQuery("input[name=SearchableText]").keyup(function () {
        PUBS.queryPublications();
    });

    // Don't warn the user that they have already submitted the form
    jQuery("#queryPublications").unbind('click');

    var recentcarousel = jQuery(".recentcarousel").jcarousel({scroll: 1});
});
