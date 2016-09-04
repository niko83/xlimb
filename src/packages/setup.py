from distutils.core import setup, Extension, Command
import pickle
import os, sys
import importlib.util
from bitarray import bitarray

class MakeData(Command):
    user_options = [
        ('generator=', None, "generator"),
        ('polygon-cell=', None, "polygon_cell"),
    ]

    def initialize_options(self):
        self.generator = None
        self.polygon_cell = None

    def finalize_options(self):
        if not self.generator or not os.path.exists(self.generator):
            print('File "%s" does not exist' % self.generator)
            sys.exit(1)

        if not self.polygon_cell or not os.path.exists(self.polygon_cell):
            print('File "%s" does not exist' % self.polygon_cell)
            sys.exit(1)


    def run(self):
        spec = importlib.util.spec_from_file_location("polygon", self.generator)
        polygon = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(polygon)

        with open('polygon_data.c_tpl') as f:
            data = f.read()

        ph1 = ''
        ph2 = ''
        for idx, points in enumerate(polygon.all_polygons):
            ph1 += "static point_list polygon%s = {%s};\n" % (
                idx,
                ','.join("{%s, %s}" % (p.x, p.y) for p in points)
            )
            ph2 += 'static Edge p%s  =   {%s, %s, %s, %s};\n' % (
                idx,
                min(p.x for p in points),
                max(p.x for p in points),
                min(p.y for p in points),
                max(p.y for p in points),
            )

        ph3 = ',\n'.join(
            '{(point_list*)polygon%s,  sizeof(polygon%s)/ sizeof(polygon%s[0]) , &p%s}' % (
                idx, idx, idx, idx
            ) for idx, _ in enumerate(polygon.all_polygons)
        )

        with open(self.polygon_cell, 'rb') as f:
            polygon_cell = pickle.load(f)

        cell_data = []
        for ys in polygon_cell:
            cell_data.append('{%s}' % (', '.join('1' if y else '0' for y in ys)))

        ph4 = 'static int polygon_cell[][%s] = {\n%s};\n' % (
            len(polygon_cell[0]),
            ', \n'.join(cell_data)
        )

        data = data.replace('//__PLACEHOLDER_1__', ph1)
        data = data.replace('//__PLACEHOLDER_2__', ph2)
        data = data.replace('//__PLACEHOLDER_3__', ph3)
        data = data.replace('//__PLACEHOLDER_4__', ph4)


        with open('polygon_data.c', 'w') as f:
            f.write(data)


setup(
    name='xlimb_helper',
    description='',
    ext_modules=[
        Extension('xlimb_helper', sources=[
            'xlimb.c',
            'helper.c',
            'polygon.c',
            'bullet.c',
        ])
    ],
    cmdclass={
        'make_data': MakeData,
    }
)
