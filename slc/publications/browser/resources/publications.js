var PUBS = {};

PUBS.queryPublications = function () {
    var query = jQuery("#publicationsFilter").serialize();
    jQuery.getJSON(
        "publications_view.json?"+query, function(data) {
            var items = [],
            results = "";
            jQuery.each(data, function(key, val) {
                var link = "<a href='"+val["path"]+"'>"+val["title"]+"</a>";
                items.push('<tr><td>'+link+'</td><td>'+val['date']+'</td><td>'+val['type']+'</td><td>'+val['size']+'</td></tr>');
            });
            results = jQuery('<tbody/>', {html:items.join('')});
            jQuery("#resultTable tbody").replaceWith(results);
        })
};

jQuery(document).ready(function() {
    jQuery("#publicationsFilter").submit(function() {
        PUBS.queryPublications()
        return false;
    });
});
