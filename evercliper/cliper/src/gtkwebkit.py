#!/usr/bin/env python
import gtk, webkit
import urlparse



def on_navigation_requested( view, frame, req, data=None):
    print type(frame)
    url = req.get_uri()
    print url
    if 'notecollecter' in url:
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        query = urlparse.urlparse(url).query
        data = dict(urlparse.parse_qsl(query))
        print data['oauth_token']
        return True
    else:
        return False
    # if 'NoteCollecter' in url.host():
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
    #     return True
    # else:
    #     return False


#
window = gtk.Window()
hbox = gtk.HBox()
vbox = gtk.VBox()
scroller = gtk.ScrolledWindow()
browser = webkit.WebView()
browser.connect("navigation-requested",on_navigation_requested)
#entry = gtk.Entry()
#button = gtk.Button('Load url')
#
window.set_title('Hello world Browser 1.0')
window.set_size_request(800, 400)
#
window.add(vbox)
scroller.add(browser)
#hbox.pack_start(entry)
#hbox.pack_start(button, False)
vbox.pack_start(hbox, False)
vbox.pack_start(scroller)
#
# def clicked_button(button):
#     url_toopen = entry.get_text()
#     print "Opening: " + url_toopen
browser.open( "https://sandbox.evernote.com/OAuth.action?oauth_token=channing.1459299A07F.687474703A2F2F4E6F7465436F6C6C65637465722F.9DE7784506C41F05E240B198520C7163" )
window.connect('destroy', lambda w: gtk.main_quit())
#button.connect('clicked', clicked_button)
#
window.show_all()
gtk.main() # This isn't necessary if we're executing this code through an interactive terminal.
