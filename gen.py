from polygon import generate_convex_polygon, generate_fractions, rotate_polygon, jsonify_vertices
from fractions import Fraction
import itertools
import numpy as np
import tqdm

import traceback


def powerset(iterable):
    s = tuple(iterable)
    combinations_iter = (itertools.combinations(s, r) for r in range(len(s)+1))
    return itertools.chain.from_iterable(combinations_iter)


def generate_polyhedron_rec(n_layers, max_den, max_vert, layer_stack=(), within=None):
    if len(layer_stack) == n_layers:
        yield layer_stack
        return

    if len(layer_stack) > n_layers:
        raise ValueError()

    if within is None:
        if len(layer_stack) == 0:
            key = ((-1,-1), (1,-1), (1,1), (-1,1))
        else:
            key = layer_stack[-1].key

        within = tuple(np.array(vertex) for vertex in key)
    
    for n_vert in range(3, max_vert+1):
        if len(layer_stack) == 0:
            polygons = set()
            with tqdm.tqdm() as pbar:
                pbar.desc = "{} vertices".format(n_vert)
                for polygon in generate_convex_polygon(n_vert,
                                                       max_den,
                                                       within,
                                                       pbar):
                    polygons.add(min(rotate_polygon(polygon.key)))
        else:
            try:
                polygons = tuple(p.key for p in generate_convex_polygon(n_vert,
                                                                        max_den,
                                                                        within))
            except ValueError as e:
                polygons = ()
                traceback.print_exc()

            assert(len(frozenset(polygons)) == len(polygons))

        if len(layer_stack) == 0:
            it = tqdm.tqdm(polygons, desc="{} vertices".format(n_vert))
        else:
            it = iter(polygons)
        for polygon_vertices in it:
            yield from generate_polyhedron_rec(n_layers,
                                               max_den,
                                               len(polygon_vertices),
                                               layer_stack + (polygon_vertices,),
                                               polygon_vertices
            )
                                               
def generate_polyhedron(max_polygon_vertices, max_denom):
    layer_heights = generate_fractions(max_denom)

    for polyhedron in generate_polyhedron_rec(len(layer_heights), max_denom,
                                       max_polygon_vertices):
        yield tuple(zip(layer_heights, polyhedron))

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
            polyhedrons = tuple(generate_polyhedron(args.nb_vertices, args.max_denom))
            json.dump([
              [(round(float(h), nb_digits), jsonify_vertices(layer, nb_digits)) for h, layer in ph]
              for ph in polyhedrons
            ], fp)
            print("{} polyhedrons generated.".format(len(polyhedrons)))
    else:
        count = 0
        for i, ph in enumerate(generate_polyhedron(args.nb_vertices, args.max_denom)):
            count += 1
        print(count)
