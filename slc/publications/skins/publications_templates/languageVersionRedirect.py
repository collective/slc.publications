##parameters=language='en'
##title=Redirect to the current objects translation

T = context.getTranslation(language)

portal_type = getattr(T, 'portal_type')

if portal_type in context.portal_properties.site_properties.typesUseViewActionInListings:
    url = T.absolute_url()+'/view'
else:
    T.absolute_url()
    
return context.REQUEST.RESPONSE.redirect(url)