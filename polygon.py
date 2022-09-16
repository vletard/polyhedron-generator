import itertools
import math
import numpy as np
from fractions import Fraction
from numbers import Number
from collections import namedtuple

Point2D = namedtuple("Point2D", ("x", "y"))

class GenericRing:
    def __init__(self, key, rotation=None):
        if rotation is None:
            self.__rotation = GenericRing.default_rotation
        else:
            self.__rotation = rotation

        self.initial_key = key
        self.__key = min(self.shift(key))
    
    def shift(self, key):
        for i in range(len(key)):
            yield from self.__rotation(key[i:] + key[:i])

    @staticmethod
    def default_rotation(x):
        yield x
    
    @property
    def key(self):
        return self.__key
    
    def __eq__(self, obj):
        return isinstance(obj, GenericRing) and obj.__key == self.__key
    
    def __hash__(self):
        return hash(self.__key)
    
    def __repr__(self):
        return "GenericRing{}".format(self.__key)


def generate_fractions(max_den):
    s = {Fraction(0), Fraction(1)}
    for den in range(1, max_den+1):
        for num in range(2, den):
            s.add(Fraction(num, den))
    return tuple(sorted(s))

def rotate_polygon(vertices):
    vertices = list(vertices)
    for _ in range(len(vertices)):
        for idx, point in enumerate(vertices):
            vertices[idx] = Point2D(-point.y, point.x)
        yield tuple(vertices)

def complete_polygon_rec(nb_vertices, highest_subdivision, enclosing_vectors, vertices, ordered_fractions):
    if len(vertices) == nb_vertices:
        if np.sign(np.cross(vertices[0]-vertices[-1], vertices[-1]-vertices[-2])) == 1:
            yield GenericRing(tuple(Point2D(v[0], v[1]) for v in vertices), rotate_polygon)
    else:
        for x, y in itertools.product(ordered_fractions, repeat=2):
            v = np.array((x*2-1, y*2-1))
            for v0 in vertices:
                if all(v == v0):
                    break
            else:
                if np.sign(np.cross(v-vertices[-1], vertices[-1]-vertices[-2])) == 1:
                    yield from complete_polygon_rec(nb_vertices, highest_subdivision, enclosing_vectors, vertices + (v,), ordered_fractions)


def generate_convex_polygon(nb_vertices, highest_subdivision, within=((-1,-1), (1,-1), (1,1), (-1,1)), pbar=None):
    if not isinstance(highest_subdivision, Number) \
      or highest_subdivision < 1 \
      or highest_subdivision % 1 != 0:
        raise ValueError(highest_subdivision)
    if not isinstance(nb_vertices, Number) \
      or nb_vertices < 3 \
      or nb_vertices % 1 != 0:
          raise ValueError(nb_vertices)
    
    generated = set()
    within = tuple(np.array(vert) for vert in within)
    enclosing_vectors = tuple(within[i] - within[i-1] for i in range(len(within)))
    if len(set(np.sign(np.cross(enclosing_vectors[i], enclosing_vectors[i-1]))
               for i in range(len(enclosing_vectors)))) > 1:
        raise ValueError("Enclosing polygon is not convex.")
    
    ordered_fractions = generate_fractions(highest_subdivision)
    if pbar is not None:
        pbar.total = len(ordered_fractions)**4
    
    for x1, y1, x2, y2 in itertools.product(ordered_fractions, repeat=4):
        if pbar is not None:
            pbar.update()

        v1 = np.array((x1*2-1, y1*2-1))
        v2 = np.array((x2*2-1, y2*2-1))
        if all(v1 == v2):
            continue
        for polygon_ring in complete_polygon_rec(nb_vertices, highest_subdivision, enclosing_vectors, (v1, v2), ordered_fractions):
            if polygon_ring not in generated:
                generated.add(polygon_ring)
                yield polygon_ring


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("nb_vertices", type=int)
    parser.add_argument("max_denom", type=int)
    parser.add_argument("--json_output", help="Name of a file for a JSON output.")
    
    args = parser.parse_args()

    if args.json_output is not None:
        import tqdm, json
        nb_digits = 6

        with open(args.json_output, "w") as fp:
            polys = tuple(generate_convex_polygon(args.nb_vertices, args.max_denom, pbar=tqdm.tqdm()))
            json.dump([[(
                    round(float(v.x), nb_digits),
                    round(float(v.y), nb_digits),
                  ) for v in poly.key]
                for poly in polys], fp)
            print("{} polygons generated.".format(len(polys)))
    else:
        for poly in generate_convex_polygon(args.nb_vertices, args.max_denom):
            print(poly.key)
