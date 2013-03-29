#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mapnik
mapnik.logger.set_severity(mapnik.severity_type.None)

import sys
import os.path
from compare import compare, compare_grids
from time import time
from reporting import Reporting

try:
    import json
except ImportError:
    import simplejson as json

visual_output_dir = "/tmp/mapnik-visual-images"

defaults = {
    'sizes': [(500, 100)],
    'scales':[1.0, 2.0],
    'agg': True,
    'cairo': True,
    'grid': False,
}

sizes_many_in_big_range = [(800, 100), (600, 100), (400, 100),
    (300, 100), (250, 100), (150, 100), (100, 100)]

sizes_few_square = [(800, 800), (600, 600), (400, 400), (200, 200)]
sizes_many_in_small_range = [(490, 100), (495, 100), (497, 100), (498, 100),
    (499, 100), (500, 100), (501, 100), (502, 100), (505, 100), (510, 100)]

default_text_box = mapnik.Box2d(-0.05, -0.01, 0.95, 0.01)

dirname = os.path.dirname(__file__)

text_tests = [
    {'name': "list", 'sizes': sizes_many_in_big_range,'bbox':default_text_box},
    {'name': "simple", 'sizes': sizes_many_in_big_range,'bbox':default_text_box},
    {'name': "lines-1", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "lines-2", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "lines-3", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "lines-4", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "lines-5", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "lines-6", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "formatting", 'bbox':default_text_box},
    # https://github.com/mapnik/mapnik/issues/1696
    # https://github.com/mapnik/mapnik/issues/1521
    # fails with clang++ on os x
    #{'name': "lines-shield", 'sizes': sizes_few_square,'bbox':default_text_box},
    {'name': "collision", 'sizes':[(600,400)]},
    {'name': "text-halo-rasterizer", 'sizes':[(600,400)]},
    {'name': "simple-E", 'bbox':default_text_box},
    {'name': "simple-NE",'bbox':default_text_box},
    {'name': "simple-NW",'bbox':default_text_box},
    {'name': "simple-N",'bbox':default_text_box},
    {'name': "simple-SE",'bbox':default_text_box},
    {'name': "simple-SW",'bbox':default_text_box},
    {'name': "simple-S",'bbox':default_text_box},
    {'name': "simple-W",'bbox':default_text_box},
    {'name': "formatting-1",'bbox':default_text_box},
    {'name': "formatting-2",'bbox':default_text_box},
    {'name': "formatting-3",'bbox':default_text_box},
    {'name': "formatting-4",'bbox':default_text_box},
    {'name': "expressionformat",'bbox':default_text_box},
    {'name': "shieldsymbolizer-1", 'sizes': sizes_many_in_small_range,'bbox':default_text_box},
    {'name': "shieldsymbolizer-2", 'bbox':default_text_box},
    {'name': "shieldsymbolizer-3", 'bbox':default_text_box},
    {'name': "shieldsymbolizer-4", 'bbox':default_text_box},
    {'name': "orientation", 'sizes': [(800, 200)], 'bbox':default_text_box},
    {'name': "hb-fontsets", 'sizes': [(800, 200)], 'bbox':default_text_box},
    {'name': "charspacing", 'sizes': [(200, 400)], 'bbox':default_text_box},
    {'name': "charspacing-lines", 'sizes': [(300, 300)], 'bbox':default_text_box},
    {'name': "line_break", 'sizes': [(800, 800)], 'bbox':default_text_box},
    {'name': "rtl-point", 'sizes': [(200, 200)],'bbox':default_text_box},
    {'name': "jalign-auto", 'sizes': [(200, 200)],'bbox':default_text_box},
    {'name': "line-offset", 'sizes':[(900, 250)],'bbox': mapnik.Box2d(-5.192, 50.189, -5.174, 50.195)},
]

tiff_tests = [
    {'name': "tiff-alpha-gdal", 'sizes':[(600,400)]},
    {'name': "tiff-alpha-broken-assoc-alpha-gdal", 'sizes':[(600,400)]},
    {'name': "tiff-alpha-gradient-gdal", 'sizes':[(600,400)]},
    {'name': "tiff-nodata-edge-gdal", 'sizes':[(600,400),(969,793)]},
    {'name': "tiff-opaque-edge-gdal", 'sizes':[(256,256),(969,793)]},
    {'name': "tiff-opaque-edge-gdal2", 'sizes':[(600,400),(969,793)]},
    {'name': "tiff-opaque-edge-raster2", 'sizes':[(600,400),(969,793)]},
    {'name': "tiff-resampling", 'sizes':[(600,400)]},
    # https://github.com/mapnik/mapnik/issues/1622
    {'name': "tiff-edge-alignment-gdal1", 'sizes':[(256,256),(255,257)],
	'bbox':mapnik.Box2d(-13267022.12540147,4618019.500877209,-13247454.246160466,4637587.380118214)
    },
    {'name': "tiff-edge-alignment-gdal2", 'sizes':[(256,256),(255,257)],
	'bbox':mapnik.Box2d(-13267022.12540147,4598451.621636203,-13247454.246160466,4618019.500877209)
    },
    # https://github.com/mapnik/mapnik/issues/1520
    # commented because these are not critical failures
    #{'name': "tiff-alpha-raster", 'sizes':[(600,400)]},
    #{'name': "tiff-alpha-broken-assoc-alpha-raster", 'sizes':[(600,400)]},
    #{'name': "tiff-nodata-edge-raster", 'sizes':[(600,400)]},
    #{'name': "tiff-opaque-edge-raster", 'sizes':[(256,256)]},
]

other_tests = [
    {'name': "marker-svg-opacity"},
    {'name': "marker-multi-policy", 'sizes':[(600,400)]},
    {'name': "marker-on-line", 'sizes':[(600,400)],
	'bbox': mapnik.Box2d(-10, 0, 15, 20)},
    {'name': "marker-on-line-spacing-eq-width", 'sizes':[(600,400)]},
    {'name': "marker-on-line-spacing-eq-width-overlap", 'sizes':[(600,400)]},
    {'name': "marker_line_placement_on_points"},
    {'name': "marker-with-background-image", 'sizes':[(600,400),(400,600),(257,256)]},
    {'name': "marker-with-background-image-and-hsla-transform", 'sizes':[(600,400),(400,600),(257,256)]},
    {'name': "marker-on-hex-grid", 'sizes':[(600,400),(400,600),(257,256)]},
    {'name': "whole-centroid", 'sizes':[(600,400)],
	'bbox': mapnik.Box2d(736908, 4390316, 2060771, 5942346)},
]

files = text_tests + tiff_tests + other_tests

def render_cairo(m, output, scale_factor):
    mapnik.render_to_file(m, output, 'ARGB32', scale_factor)
    # open and re-save as png8 to save space
    new_im = mapnik.Image.open(output)
    new_im.save(output, 'png8:m=h')

def render_grid(m, output, scale_factor):
    grid = mapnik.Grid(m.width, m.height)
    mapnik.render_layer(m, grid, layer=0)
    utf1 = grid.encode('utf', resolution=4)
    open(output,'wb').write(json.dumps(utf1, indent=1))

            
renderers = [
    { 'name': 'agg',
      'render': lambda m, output, scale_factor: mapnik.render_to_file(m, output, 'png8:m=h', scale_factor),
      'compare': lambda actual, reference: compare(actual, reference, alpha=True),
      'threshold': 0,
      'filetype': 'png',
      'dir': 'images'
    },
    { 'name': 'cairo',
      'render': render_cairo,
      'compare': lambda actual, reference: compare(actual, reference, alpha=False),
      'threshold': 0,
      'filetype': 'png',
      'dir': 'images'
    },
    { 'name': 'grid',
      'render': render_grid,
      'compare': lambda actual, reference: compare_grids(actual, reference, alpha=False),
      'threshold': 0,
      'filetype': 'json',
      'dir': 'grids'
    }
]


def render(m, config, width, height, scale_factor, reporting):
    filename = config['name']
    postfix = "%s-%d-%d-%s" % (filename, width, height, scale_factor)

    bbox = config.get('bbox')
    m.resize(int(width*scale_factor), int(height*scale_factor))
    if bbox is not None:
        m.zoom_to_box(bbox)
    else:
        m.zoom_all()
    
    for renderer in renderers:
        # TODO - grid renderer does not support scale_factor yet via python
        if renderer['name'] == 'grid' and scale_factor != 1.0:
            continue
        if config.get(renderer['name'], True):
            expected = os.path.join(dirname, renderer['dir'], '%s-%s-reference.%s' %
                (postfix, renderer['name'], renderer['filetype']))
            actual = os.path.join(visual_output_dir, '%s-%s.%s' %
                (postfix, renderer['name'], renderer['filetype']))
            if not quiet:
                print "\"%s\" with %s..." % (postfix, renderer['name']),
            try:
                start = time()
                renderer['render'](m, actual, scale_factor)
                render_time = time() - start
                
                if not os.path.exists(expected):
                    reporting.not_found(actual, expected)
                else:
                    diff = renderer['compare'](actual, expected)
                    if diff > renderer['threshold']:
                        reporting.result_fail(actual, expected, diff, render_time)
                    else:
                        reporting.result_pass(actual, expected, diff, render_time)
            except Exception, e:
                reporting.other_error('%s-%s' % (postfix, renderer['name']), repr(e))

if __name__ == "__main__":
    if '-q' in sys.argv:
        quiet = True
        sys.argv.remove('-q')
    else:
        quiet = False

    if '--overwrite' in sys.argv:
        overwrite_failures = True
        sys.argv.remove('--overwrite')
    else:
        overwrite_failures = False

    if '--no-generate' in sys.argv:
        generate = False
        sys.argv.remove('--no-generate')
    else:
        generate = True

    if len(sys.argv) == 2:
        files = [{"name": sys.argv[1], "sizes": sizes_few_square}]
    elif len(sys.argv) > 2:
        files = []
        for name in sys.argv[1:]:
            files.append({"name": name})

    if not os.path.exists(visual_output_dir):
        os.makedirs(visual_output_dir)


    if 'osm' in mapnik.DatasourceCache.plugin_names():
        reporting = Reporting(quiet=quiet, generate=generate, overwrite_failures=overwrite_failures)
        for f in files:
            config = dict(defaults)
            config.update(f)
            m = mapnik.Map(16, 16)
            try:
                start = time()
                mapnik.load_map(m, os.path.join(dirname, "styles", "%s.xml" % config['name']), False)
            except Exception, e:
                reporting.load_error(filename, repr(e))

            for size in config['sizes']:
                for scale_factor in config['scales']:
                    render(m, config,
                               size[0],
                               size[1],
                               scale_factor,
                               reporting)
            mapnik.save_map(m, os.path.join(dirname, 'xml_output', "%s-out.xml" % config['name']))

        sys.exit(reporting.summary())
    else:
        print "OSM plugin required"
