=== Plugin Name ===
name=Compotte
author=Jan Bojko
email=jan.bojko@gmail.com
homepage=www.ccss.cz
repository=http://redmine.ccss.cz/projects/compotte/repository
wiki=http://redmine.ccss.cz/projects/compotte/wiki

=== Installation ===

This section describes how to install the plugin and get it working.

1. Download an archive
2. Uncompress the archive
3. Copy whole compotte folder to the QGIS plugin folder e.g.:
	* Windows hosts: c:\Program Files\QGIS Dufour\apps\qgis\python\plugins\compotte
	* Linux: /home/myuser/.qgis2/python/plugins/compotte
4. Start/Restart QGIS and the plugin should show up in the "Plugin -> Manage and Install Plugins..."

=== Test Compositions ===
The composition may have a difficult format, the map compositions from the "../compotte/test" folder could help you clarify the format. Please feel free to contact authors if something goes wrong.

=== Changelog ===

= 0.1 =
* First version
= 0.2 =
- new service dialog
- cas authentication
- temporary folder option

=== Python libraries ===
BeautifulSoup 3.2.1
Requests 2.3.0
Qt4