#Author-David Watson.
#Description-Import airfoil from xml file https://www.mh-aerotools.de/airfoils/

from re import S
import adsk.core, adsk.fusion, traceback
import io
from xml.dom import minidom

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # Get all components in the active design.
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        title = 'Import Airfoil XML'
        if not design:
            ui.messageBox('No active Fusion design', title)
            return
        
        dlg = ui.createFileDialog()
        dlg.title = 'Open XML File'
        dlg.filter = 'XML (*.xml);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
            return
        
        filename = dlg.filename
        points = adsk.core.ObjectCollection.create()
        airfoil_dom = minidom.parse(filename)
        airfoil = airfoil_dom.documentElement
        scale = get_scale(airfoil)

        points_list = get_points(airfoil)
        for point_data in points_list:
            x = point_data['x'] * scale['x']
            y = point_data['y'] * scale['y']
            z = point_data['z'] * scale['z']
            point = adsk.core.Point3D.create(x, y, z)
            points.add(point)

        if points.count:
            root = design.rootComponent
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.sketchCurves.sketchFittedSplines.add(points)
        else:
            ui.messageBox('No valid points', title)            
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def get_points(airfoil):
    coordinates_list = airfoil.getElementsByTagName('coordinates')
    coordinates = coordinates_list[0]
    return list(map(convert_point_data, coordinates.getElementsByTagName('point')))


def convert_point_data(point_data):
    point = {}
    point['x'] = float(point_data.getElementsByTagName('x')[0].childNodes[0].data)
    point['y'] = float(point_data.getElementsByTagName('y')[0].childNodes[0].data)
    point['z'] = float(point_data.getElementsByTagName('z')[0].childNodes[0].data)
    return point


def get_scale(airfoil):
    scale_list = airfoil.getElementsByTagName('scaling')
    scale = scale_list[0]
    scale_data= scale.getElementsByTagName('point')[0]
    scale = {}
    scale['x'] = float(scale_data.getElementsByTagName('x')[0].childNodes[0].data)
    scale['y'] = float(scale_data.getElementsByTagName('y')[0].childNodes[0].data)
    scale['z'] = float(scale_data.getElementsByTagName('z')[0].childNodes[0].data)
    return scale