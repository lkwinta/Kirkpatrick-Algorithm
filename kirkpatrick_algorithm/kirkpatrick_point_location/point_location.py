from scipy.spatial import Delaunay,delaunay_plot_2d
from planegeometry.structures.planarmaps import PlanarMap, Point, Segment, Triangle
from collections import deque
from typing import List
import mapbox_earcut as earcut
import numpy as np
from kirkpatrick_algorithm.visualizer.main import Visualizer

class Kirkpatrick: 
    def __init__(self, polygon: List[tuple[float, float]]):
        """
            Konstruktor klasy Kirkpatrick. Inicjalizuje wszystkie pola potrzebne do działania biblioteki.
            Dodaje zewnętrzny trójkąt, następnie wykonuje triangulację Delaunaya, a na końcu konwertuje
            wielokąt do postaci listy sąsiedztwa.

            Parmeters
            ---------
                polygon: `List[tuple[float, float]]`
                    lista krotek oznaczających współrzędne kolejnych punktów wielokąta
        """
        self.__original_polygon = polygon

        outer_triangle = self.__add_outer_triangle(polygon)
        self.__polygon_with_triangle = self.__original_polygon + outer_triangle

        outer_triangle = [Point(x, y) for x, y in outer_triangle]

        self.__root_triangle = Triangle(outer_triangle[0], outer_triangle[1], outer_triangle[2])
        self.__outer_triangle = set(outer_triangle)

        self.__delaunay_triangulation = Delaunay(self.__polygon_with_triangle)
        self.__polygon_planar_map = self.__get_planar_map(self.__delaunay_triangulation)

        self.__preproccessed = False

        self.__triangles_graph = {}
        self.__triangles_list = []
    
    def __add_outer_triangle(self, polygon: List[tuple[float, float]]) -> List[tuple[float, float]]:
        """
            Oblicza współrzędne wierzchołków trójkąta zawierającego wszystkie punkty wielokąta

            Parameters
            ----------
                polygon: `List[tuple[float, float]]`
                    lista krotek oznaczających współrzędne kolejnych punktów wielokąta

            Returns
            -------
                `List[tuple[float, float]]`: lista wierzchołków zewnętrznego trójkąta
        """
        min_x = min(polygon, key=lambda p: p[0])[0]
        max_x = max(polygon, key=lambda p: p[0])[0]
        min_y = min(polygon, key=lambda p: p[1])[1]
        max_y = max(polygon, key=lambda p: p[1])[1]

        a = (max_x - min_x)
        b = (max_y - min_y)

        min_x -= a*0.4
        max_x += a*0.4
        min_y -= b*0.4
        max_y += b*0.4

        a = (max_x - min_x)
        b = (max_y - min_y)

        sqrt_d = np.sqrt(4/3*b*b)

        d = (2*a + sqrt_d)/2

        shift = (d - a)/2
        H = d*np.sqrt(3)/2

        return [(max_x + shift, min_y),(min_x - shift, min_y), ((max_x - min_x)/2 + min_x, min_y + H)]
    
    def __get_planar_map(self, delaunay: Delaunay) -> PlanarMap:
        """
        Konwertuje striangulowany wielokąt do postaci listy sąsiedztwa w obiekcie typu `PlanarMap`

        Parameters
        ----------
            delaunay: `Delaunay`
                striangulowany wielokąt w obiekcie typu `Delaunay` z biblioteki `SciPy` 

        Returns
        -------
            `PlanarMap`: reprezentacja wielokąta za pomocą listy sąsiedztwa
        """
        set_of_edges = set()
        points = [Point(p[0], p[1]) for p in delaunay.points]

        get_edge = lambda a, b: (min(a, b), max(a, b))

        for a, b, c in delaunay.simplices:
            set_of_edges.add(get_edge(a, b))
            set_of_edges.add(get_edge(b, c))
            set_of_edges.add(get_edge(a, c))

        segments = [Segment(points[a], points[b]) for a, b in set_of_edges]

        dcel_map = PlanarMap(segments[0])
        for i in range(1, len(segments)):
            dcel_map.add_edge(segments[i])

        return dcel_map
    
    def __get_independent_set(self) -> List[Point]:
        """
        Oblicza zbiór niezależnych punktów z wielokąta
        
        Parameters
        ----------
            `None`

        Returns
        -------
            `List[Point]`: lista punktów tworzących zbiór niezależny
        """
        visited = set()
        independent_set = []

        for point in self.__polygon_planar_map.iterpoints():
            if point not in visited and point not in self.__outer_triangle:
                independent_set.append(point)
                
                for adjacent_point in self.__polygon_planar_map.iteradjacent(point):
                    visited.add(adjacent_point)

        return independent_set
    
    def __remove_independent_set(self, indepndent_set: List[Point]) -> (List[List[Point]], int, List[List[Triangle]]):
        """
        Usuwa zbiór niezależnych punktów z wielokąta
        
        Parameters
        ----------
            indepndent_set: `List[Point]`
                lista punktów tworzących zbiór niezależnych punktów

        Returns
        -------
            `List[List[Point]]`: lista punktów tworzących dziurę powstałą przez 
            'int': ilość usuniętych wierzchołków
            `List[List[Triangle]]`: lista usuniętych trójkątów
        """
        holes = []
        removed_triangles = []
        deleted_nodes = 0

        for independent_point in indepndent_set:
            if independent_point not in self.__outer_triangle:
                outedges = sorted(list(self.__polygon_planar_map.iteroutedges(independent_point)), key=lambda e: (e.target - e.source).alpha())
                holes.append([outedge.target for outedge in outedges])
                removed_triangles.append([])
                for i in range(len(holes[-1])):
                    removed_triangles[-1].append(Triangle(independent_point, holes[-1][i-1], holes[-1][i]))

                self.__polygon_planar_map.del_node(independent_point)
                deleted_nodes += 1

        return holes, deleted_nodes, removed_triangles
    
    def __triangle_intersect(self, t1: Triangle, t2: Triangle) -> bool:
        """
        Sprawdza czy dwa tójkąty nakładają się na siebie
        
        Parameters
        ----------
            t1: `Triangle`
                pierwszy trójkąt
            t2: `Triangle`
                drugi trójkąt

        Returns
        -------
            `bool`: wartość logiczna mówiąca czy trójkąty mają część wspólną
        """
        for t1_segment in t1.itersegments():
            for t2_segment in t2.itersegments():
                if t1_segment.intersect(t2_segment):
                    return True
                
        return False

    def preprocess(self):
        """
        Przetwarza wielokąt budując drzewo przeszukiwania
        
        Parameters
        ----------
            `None`

        Returns
        -------
            `None`
        
        Raises
        ------
            `Exception` jeśli próbowano wywyołać przetwarzanie więcej niż raz
        """
        if self.__preproccessed:
            raise Exception("Already preproccessed")
        
        v = len(self.__polygon_with_triangle)

        for a, b, c in self.__delaunay_triangulation.simplices:
            triangle = Triangle(Point(self.__polygon_with_triangle[a][0], self.__polygon_with_triangle[a][1]),
                                Point(self.__polygon_with_triangle[b][0], self.__polygon_with_triangle[b][1]),
                                Point(self.__polygon_with_triangle[c][0], self.__polygon_with_triangle[c][1]))
            
            self.__triangles_list.append(triangle)
            self.__triangles_graph[triangle] = []


        while v > 3:
            independent_set = self.__get_independent_set()
            holes_points, removed, all_removed_triangles = self.__remove_independent_set(independent_set)

            v -= removed

            for hole_points, removed_triangles in zip(holes_points, all_removed_triangles):
                verts = np.array([[point.x, point.y] for point in hole_points]).reshape(-1, 2)
                rings = np.array([len(verts)])
                result = earcut.triangulate_float64(verts, rings)

                for a, b, c in result.reshape(-1,3):
                    new_triangle = Triangle(hole_points[a], hole_points[b], hole_points[c])

                    for segment in new_triangle.itersegments():
                        if not self.__polygon_planar_map.has_edge(segment):
                            self.__polygon_planar_map.add_edge(segment)

                    if not new_triangle in self.__triangles_graph:
                        self.__triangles_graph[new_triangle] = []
                        
                    for old_triangle in removed_triangles:
                        if self.__triangle_intersect(new_triangle, old_triangle):
                            self.__triangles_graph[new_triangle].append(old_triangle)
                    
        self.__preproccessed = True
    
    def get_triangles(self) -> List[Triangle]:
        """
        Zwraca listę striangulowanych trójkątów
        
        Parameters
        ----------
            `None`
        Returns
        -------
            `List[Triangle]`: lista wszystkich trójkątów po pierwszej triangulacji
        """
        return self.__triangles_list

    def query(self, point: (float, float)) -> Triangle:
        """
        Przeszukuje drzewo trójkątów
        
        Parameters
        ----------
            point: `(float, float)`
                Punkt do przeszukiwań

        Returns
        -------
            `Triangle`: Znaleziony trójkąt

        Raises
        ------
            `Exception`: jeśli próbowano wywyołać przeszukiwanie bez wcześniejszego przetworzenia
        """
        if not self.__preproccessed:
            raise Exception("Polygon is not preproccessed")
        
        point = Point(point[0], point[1])

        if not point in self.__root_triangle:
            return None
        
        current = self.__root_triangle
        while self.__triangles_graph[current]:
            for triangle in self.__triangles_graph[current]:
                if point in triangle:
                    current = triangle
                    break

        return current
    
    def query_with_show(self, point: (float, float)):
        """
        Przeszukuje drzewo trójkątów, i rysuje wynik zawierający:
            - przeszukiwany punkt 
            - wielokąt z zewnętrznym trójkątem i triangulacją
            - podświetlony na żółto znaleziony trójkąt
        
        Parameters
        ----------
            point: `(float, float)`
                Punkt do przeszukiwań

        Returns
        -------
            `None`

        Raises
        ------
            `Exception`: jeśli próbowano wywyołać przeszukiwanie bez wcześniejszego przetworzenia
        """
        vis = Visualizer()
        t = self.query(point)
        if t is not None:
            vis.add_polygon([(t.pt1.x, t.pt1.y), (t.pt2.x, t.pt2.y), (t.pt3.x, t.pt3.y)], color="yellow")
        
        vis.add_point(point, zorder=10)
        for t in self.__triangles_list:
            vis.add_polygon([(t.pt1.x, t.pt1.y), (t.pt2.x, t.pt2.y), (t.pt3.x, t.pt3.y)], fill=False, color="blue")

        vis.show()
