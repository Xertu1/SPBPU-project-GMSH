from __future__ import annotations
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any
Vector = list[float]

def number_text(x: float) -> str:
    x = float(x)
    if abs(x - round(x)) < 1e-10:
        return str(int(round(x)))
    return str(round(x, 12)).replace(',', '.')

def to_float(text: Any) -> float:
    return float(str(text).strip().replace(',', '.'))

def to_int(text: Any) -> int:
    return int(round(to_float(text)))

def ask_str(prompt: str, default: str | None=None) -> str:
    suffix = f' [{default}]' if default is not None else ''
    while True:
        value = input(f'{prompt}{suffix}: ').strip()
        if value == '' and default is not None:
            return default
        if value != '':
            return value
        print('Введите значение.')

def ask_float(prompt: str, default: float | None=None, *, min_value: float | None=None, max_value: float | None=None, allow_zero: bool=True) -> float:
    default_text = None if default is None else number_text(default)
    while True:
        try:
            value = to_float(ask_str(prompt, default_text))
            if min_value is not None:
                if allow_zero:
                    if value < min_value:
                        raise ValueError
                elif value <= min_value:
                    raise ValueError
            if max_value is not None and value > max_value:
                raise ValueError
            return value
        except ValueError:
            print('Ошибка: введите корректное число в допустимом диапазоне.')

def ask_int(prompt: str, default: int | None=None, *, min_value: int | None=None, max_value: int | None=None) -> int:
    default_text = None if default is None else str(default)
    while True:
        try:
            value = to_int(ask_str(prompt, default_text))
            if min_value is not None and value < min_value:
                raise ValueError
            if max_value is not None and value > max_value:
                raise ValueError
            return value
        except ValueError:
            print('Ошибка: введите целое число в допустимом диапазоне.')

def ask_vector(prompt: str, default: Vector) -> Vector:
    default_text = ','.join((number_text(x) for x in default))
    while True:
        raw = ask_str(prompt + ' (три числа через запятую)', default_text)
        try:
            parts = raw.replace(';', ',').split(',')
            if len(parts) != 3:
                raise ValueError
            v = [to_float(parts[0]), to_float(parts[1]), to_float(parts[2])]
            if norm(v) <= 1e-14:
                raise ValueError
            return v
        except ValueError:
            print('Ошибка: нужен ненулевой вектор вида 0,0,1')

def ask_yes_no(prompt: str, default: bool=True) -> bool:
    default_text = 'д' if default else 'н'
    while True:
        value = ask_str(prompt + ' (д/н)', default_text).lower()
        if value in {'д', 'да', 'y', 'yes'}:
            return True
        if value in {'н', 'нет', 'n', 'no'}:
            return False
        print('Ответьте д или н.')

def dot(a: Any, b: Any) -> float:
    return float(a[0] * b[0] + a[1] * b[1] + a[2] * b[2])

def cross(a: Any, b: Any) -> Vector:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

def add(a: Any, b: Any) -> Vector:
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

def sub(a: Any, b: Any) -> Vector:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def mul(k: float, v: Any) -> Vector:
    return [k * v[0], k * v[1], k * v[2]]

def norm(v: Any) -> float:
    return math.sqrt(dot(v, v))

def normalization(v: Any) -> Vector:
    n = norm(v)
    if n <= 1e-14:
        raise ValueError('Нулевой вектор нельзя нормировать')
    return [v[0] / n, v[1] / n, v[2] / n]

def rotate_vec(v: Any, axis: Any, theta_deg: float) -> Vector:
    axis = normalization(axis)
    theta = math.radians(theta_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    return add(add(mul(c, v), mul(s, cross(axis, v))), mul(dot(axis, v) * (1 - c), axis))

def vector_text(v: Any) -> str:
    return '{' + ', '.join((number_text(float(x)) for x in v)) + '}'

def angle_rad_text(angle_deg: float) -> str:
    frac = Fraction(angle_deg / 180.0).limit_denominator(360)
    if abs(float(frac) - angle_deg / 180.0) < 1e-12:
        n, d = (frac.numerator, frac.denominator)
        if n == 0:
            return '0'
        sign = '-' if n < 0 else ''
        n = abs(n)
        if d == 1:
            return sign + ('Pi' if n == 1 else f'{n}*Pi')
        return sign + (f'Pi/{d}' if n == 1 else f'{n}*Pi/{d}')
    return number_text(math.radians(angle_deg))

def layer_fractions(n: int, grading: float) -> list[float]:
    if n < 1:
        raise ValueError('Количество слоёв должно быть >= 1')
    if grading <= 0:
        raise ValueError('Сгущение должно быть > 0')
    if abs(grading - 1.0) < 1e-12 or n == 1:
        return [(i + 1) / n for i in range(n)]
    q = (1.0 / grading) ** (1.0 / max(1, n - 1))
    sizes = [q ** i for i in range(n)]
    total = sum(sizes)
    acc = 0.0
    result: list[float] = []
    for size in sizes:
        acc += size / total
        result.append(acc)
    result[-1] = 1.0
    return result

def fractions_text(values: list[float]) -> str:
    return '{' + ', '.join((number_text(v) for v in values)) + '}'

def layers_geo_text(n: int, grading: float) -> str:
    fractions = layer_fractions(n, grading)
    if abs(grading - 1.0) < 1e-12:
        return f'Layers{{{n}}}'
    counts = '{' + ', '.join(('1' for _ in range(n))) + '}'
    return f'Layers{{{counts}, {fractions_text(fractions)}}}'

def perpendicular_vector(v: Vector) -> Vector:
    vn = normalization(v)
    base = [1.0, 0.0, 0.0]
    if abs(dot(vn, base)) > 0.9:
        base = [0.0, 1.0, 0.0]
    return normalization(cross(vn, base))

def make_bend_compatible(tangent: Vector, axis_direction: Vector, preferred_radius_direction: Vector) -> tuple[Vector, Vector, list[str]]:
    warnings: list[str] = []
    t = normalization(tangent)
    axis_raw = normalization(axis_direction)
    axis = sub(axis_raw, mul(dot(axis_raw, t), t))
    if norm(axis) < 1e-10:
        axis = perpendicular_vector(t)
        warnings.append('Ось поворота была почти параллельна текущей трубе; выбрана безопасная перпендикулярная ось.')
    else:
        if abs(dot(axis_raw, t)) > 1e-06:
            warnings.append('Ось поворота не была перпендикулярна текущей трубе; она автоматически спроецирована в допустимое положение.')
        axis = normalization(axis)
    radius_dir = normalization(cross(axis, t))
    preferred = sub(preferred_radius_direction, mul(dot(preferred_radius_direction, axis), axis))
    if norm(preferred) > 1e-10:
        preferred = normalization(preferred)
        if dot(radius_dir, preferred) < 0:
            axis = mul(-1.0, axis)
            radius_dir = mul(-1.0, radius_dir)
    return (axis, radius_dir, warnings)

def estimate_hex_count(mesh: 'MeshSettings', segments: list['Segment']) -> int:
    cross_cells = mesh.core_cells * mesh.core_cells + 4 * mesh.core_cells * mesh.radial_cells
    axial = sum((max(1, int(seg.layers)) for seg in segments))
    return cross_cells * axial

@dataclass
class MeshSettings:
    radius: float
    diamond_half_diagonal: float
    core_cells: int
    radial_cells: int
    radial_grading: float

@dataclass
class StraightSegment:
    name: str
    length: float
    direction: Vector
    layers: int
    axial_grading: float

@dataclass
class BendSegment:
    name: str
    curvature_radius: float
    axis_direction: Vector
    radius_direction: Vector
    angle_deg: float
    layers: int
    axial_grading: float
Segment = StraightSegment | BendSegment

def choose_layers(length: float, diameter: float, default_step_diameters: float=0.5) -> int:
    print(f'Расчётная длина участка: {number_text(length)}. Диаметр трубы: {number_text(diameter)}.')
    if ask_yes_no('Задать шаг вдоль трубы через долю/количество диаметров', True):
        step_d = ask_float('Шаг вдоль трубы (0.1 = мелко, 5 = грубо)', default_step_diameters, min_value=0.1, max_value=5.0)
        return max(1, int(math.ceil(length / (step_d * diameter))))
    return ask_int('Количество слоёв вдоль этого участка', max(1, int(math.ceil(length / (default_step_diameters * diameter)))), min_value=1)

def read_user_settings() -> tuple[MeshSettings, list[Segment], str]:
    print('\nГеометрия поперечного сечения и сетка')
    diameter = ask_float('Диаметр трубы', 2.0, min_value=0.0, allow_zero=False)
    radius = diameter / 2.0
    diamond_diag = ask_float('Длина диагонали ромба внутри круга', 0.8 * radius * 2.0, min_value=0.0, max_value=diameter * 0.999, allow_zero=False)
    diamond_half = diamond_diag / 2.0
    core_cells = ask_int('Сколько квадратиков на одну сторону ромба-ядра', 8, min_value=1)
    radial_cells = ask_int('Сколько прямоугольников от ромба до стенки круга', 12, min_value=1)
    radial_grading = ask_float('Сгущение к стенке круга (1 = равномерно, 2 = мельче у стенки)', 1.2, min_value=0.0, allow_zero=False)
    mesh = MeshSettings(radius, diamond_half, core_cells, radial_cells, radial_grading)
    print('\nУчастки трубы')
    count = ask_int('Количество участков трубы', 3, min_value=1)
    segments: list[Segment] = []
    current_tangent: Vector = [0.0, 0.0, 1.0]
    diameter_value = 2.0 * radius
    for i in range(1, count + 1):
        print(f'\nУчасток {i}')
        seg_type = ask_str('Тип участка: 1 = прямая, 2 = поворот', '1' if i != 2 else '2')
        while seg_type not in {'1', '2'}:
            seg_type = ask_str('Введите 1 для прямой или 2 для поворота', '1')
        if seg_type == '1':
            length = ask_float('Длина прямого участка', 10.0 if i == 1 else 20.0, min_value=0.0, allow_zero=False)
            direction = ask_vector('Направление прямого участка', current_tangent)
            direction = normalization(direction)
            layers = choose_layers(length, diameter_value)
            axial_grading = ask_float('Сгущение вдоль этого участка (1 = равномерно, >1 = мельче к концу, <1 = мельче к началу)', 1.0, min_value=0.0, allow_zero=False)
            segments.append(StraightSegment(f'straight_{i}', length, direction, layers, axial_grading))
            current_tangent = direction
        else:
            curvature_radius = ask_float('Радиус поворота по оси трубы', 10.0 * radius, min_value=0.0, allow_zero=False)
            axis_direction = normalization(ask_vector('Ось вращения поворота', [0.0, 1.0, 0.0]))
            radius_direction = normalization(ask_vector('Направление от начала поворота к центру кривизны', [1.0, 0.0, 0.0]))
            angle_deg = ask_float('Угол поворота в градусах', 45.0, min_value=-180.0, max_value=180.0)
            while abs(angle_deg) < 1e-12:
                print('Угол поворота не должен быть нулевым.')
                angle_deg = ask_float('Угол поворота в градусах', 45.0, min_value=-180.0, max_value=180.0)
            arc_length = abs(math.radians(angle_deg) * curvature_radius)
            layers = choose_layers(arc_length, diameter_value)
            axial_grading = ask_float('Сгущение вдоль поворота (1 = равномерно, >1 = мельче к концу, <1 = мельче к началу)', 1.0, min_value=0.0, allow_zero=False)
            segments.append(BendSegment(f'bend_{i}', curvature_radius, axis_direction, radius_direction, angle_deg, layers, axial_grading))
            current_tangent = normalization(rotate_vec(current_tangent, axis_direction, angle_deg))
    output_file = ask_str('Имя выходного GEO-файла', 'pipe.geo')
    return (mesh, segments, output_file)

def cross_section_basis(normal: Vector) -> tuple[Vector, Vector]:
    n = normalization(normal)
    ref = [0.0, 0.0, 1.0]
    if abs(dot(n, ref)) > 0.9:
        ref = [0.0, 1.0, 0.0]
    u = normalization(cross(ref, n))
    v = normalization(cross(n, u))
    return (u, v)

def point_on_section(center: Vector, u: Vector, v: Vector, x: float, y: float) -> Vector:
    return add(center, add(mul(x, u), mul(y, v)))

def point_geo(tag: int, p: Vector) -> str:
    return f'Point({tag}) = {{{number_text(p[0])}, {number_text(p[1])}, {number_text(p[2])}, 1.0}};'

def add_cross_section(lines: list[str], mesh: MeshSettings, initial_tangent: Vector) -> list[str]:
    r = mesh.radius
    a = mesh.diamond_half_diagonal
    core_pts = mesh.core_cells + 1
    radial_pts = mesh.radial_cells + 1
    u, v = cross_section_basis(initial_tangent)
    c = [0.0, 0.0, 0.0]
    p1 = c
    p2 = point_on_section(c, u, v, 0.0, r)
    p3 = point_on_section(c, u, v, -r, 0.0)
    p4 = point_on_section(c, u, v, 0.0, -r)
    p5 = point_on_section(c, u, v, r, 0.0)
    p6 = point_on_section(c, u, v, 0.0, a)
    p7 = point_on_section(c, u, v, -a, 0.0)
    p8 = point_on_section(c, u, v, 0.0, -a)
    p9 = point_on_section(c, u, v, a, 0.0)
    wall_progression = (1.0 / mesh.radial_grading) ** (1.0 / max(1, mesh.radial_cells - 1))
    lines += [
    'SetFactory("OpenCASCADE");',
    'Mesh.RecombineAll = 1;',
    'Mesh.Algorithm = 8;',
    'Mesh.SubdivisionAlgorithm = 1;',
    'Geometry.Points = 0;',
    'Geometry.PointNumbers = 0;',
    'Geometry.CurveNumbers = 0;',
    'Geometry.SurfaceNumbers = 0;',
    'Mesh.Nodes = 0;',
    'Mesh.NodeLabels = 0;',
    '',

    point_geo(1, p1),
    point_geo(2, p2),
    point_geo(3, p3),
    point_geo(4, p4),
    point_geo(5, p5),
    point_geo(6, p6),
    point_geo(7, p7),
    point_geo(8, p8),
    point_geo(9, p9),
    '',

    'Circle(10) = {2, 1, 3};',
    'Circle(11) = {3, 1, 4};',
    'Circle(12) = {4, 1, 5};',
    'Circle(13) = {5, 1, 2};',
    '',

    'Line(20) = {6, 2};',
    'Line(21) = {7, 3};',
    'Line(22) = {8, 4};',
    'Line(23) = {9, 5};',
    '',

    'Line(30) = {9, 6};',
    'Line(31) = {6, 7};',
    'Line(32) = {7, 8};',
    'Line(33) = {8, 9};',
    '',

    'Curve Loop(1) = {31, 21, -10, -20};',
    'Plane Surface(1) = {1};',

    'Curve Loop(2) = {32, 22, -11, -21};',
    'Plane Surface(2) = {2};',

    'Curve Loop(3) = {33, 23, -12, -22};',
    'Plane Surface(3) = {3};',

    'Curve Loop(4) = {30, 20, -13, -23};',
    'Plane Surface(4) = {4};',

    'Curve Loop(5) = {30, 31, 32, 33};',
    'Plane Surface(5) = {5};',
    '',

    f'Transfinite Curve {{10, 11, 12, 13, 30, 31, 32, 33}} = {core_pts};',
    f'Transfinite Curve {{20, 21, 22, 23}} = {radial_pts} Using Progression {number_text(wall_progression)};',

    'Transfinite Surface {1} = {6, 7, 3, 2};',
    'Transfinite Surface {2} = {7, 8, 4, 3};',
    'Transfinite Surface {3} = {8, 9, 5, 4};',
    'Transfinite Surface {4} = {9, 6, 2, 5};',
    'Transfinite Surface {5} = {9, 6, 7, 8};',

    'Recombine Surface {1, 2, 3, 4, 5};',
    '',
]
    return ['1', '2', '3', '4', '5']

def geo_surface_list(surfaces: list[str]) -> str:
    return ', '.join(surfaces)

def extrude_output_surfaces(array_name: str, count: int) -> list[str]:
    return [f'{array_name}[{6 * i}]' for i in range(count)]

def add_straight_extrude(lines: list[str], name: str, surfaces: list[str], vec: Vector, layers: int, grading: float) -> list[str]:
    layers_text = layers_geo_text(layers, grading)
    arr = f'{name}_out'
    lines.append(f'{arr}[] = Extrude {vector_text(vec)} {{')
    lines.append(f'  Surface{{{geo_surface_list(surfaces)}}}; {layers_text}; Recombine;')
    lines.append('};')
    return extrude_output_surfaces(arr, len(surfaces))

def add_bend_extrude(lines: list[str], name: str, surfaces: list[str], axis: Vector, center: Vector, angle_deg: float, layers: int, grading: float) -> list[str]:
    layers_text = layers_geo_text(layers, grading)
    arr = f'{name}_out'
    lines.append(f'{arr}[] = Extrude {{{vector_text(axis)}, {vector_text(center)}, {angle_rad_text(angle_deg)}}} {{')
    lines.append(f'  Surface{{{geo_surface_list(surfaces)}}}; {layers_text}; Recombine;')
    lines.append('};')
    return extrude_output_surfaces(arr, len(surfaces))

def make_geo_text(mesh: MeshSettings, segments: list[Segment]) -> str:
    if not 0 < mesh.diamond_half_diagonal < mesh.radius:
        raise ValueError('Ромб должен быть меньше радиуса трубы.')
    initial_tangent: Vector = [0.0, 0.0, 1.0]
    if segments and isinstance(segments[0], StraightSegment):
        initial_tangent = normalization(segments[0].direction)
    lines: list[str] = []
    current_surfaces = add_cross_section(lines, mesh, initial_tangent)
    point_on_axis: Vector = [0.0, 0.0, 0.0]
    tangent: Vector = initial_tangent[:]
    for segment in segments:
        lines.append('')
        lines.append(f'// Участок {segment.name}')
        if isinstance(segment, StraightSegment):
            direction = normalization(segment.direction)
            vec = mul(segment.length, direction)
            current_surfaces = add_straight_extrude(lines, segment.name, current_surfaces, vec, segment.layers, segment.axial_grading)
            point_on_axis = add(point_on_axis, vec)
            tangent = direction
        else:
            axis, radius_dir, warnings = make_bend_compatible(tangent, segment.axis_direction, segment.radius_direction)
            curvature_radius = segment.curvature_radius
            if curvature_radius <= mesh.radius * 1.001:
                old_radius = curvature_radius
                curvature_radius = mesh.radius * 1.001
                warnings.append('Радиус поворота был меньше/равен радиусу трубы; увеличен до безопасного минимума ' + number_text(curvature_radius) + ' вместо ' + number_text(old_radius) + '.')
            for warning in warnings:
                lines.append('// АВТОИСПРАВЛЕНИЕ: ' + warning)
            center = add(point_on_axis, mul(curvature_radius, radius_dir))
            current_surfaces = add_bend_extrude(lines, segment.name, current_surfaces, axis, center, segment.angle_deg, segment.layers, segment.axial_grading)
            point_on_axis = add(center, rotate_vec(sub(point_on_axis, center), axis, segment.angle_deg))
            tangent = normalization(rotate_vec(tangent, axis, segment.angle_deg))
    lines += ['', 'Coherence;', 'Recombine Surface "*";', 'Recombine Volume "*";', '// Mesh 3; специально НЕ включён, чтобы Gmsh не закрывался при открытии файла.', '// Для построения сетки нажмите в Gmsh: Mesh -> 3D или запустите: gmsh pipe.geo -3']
    return '\n'.join(lines) + '\n'

def make_demo() -> tuple[MeshSettings, list[Segment]]:
    mesh = MeshSettings(radius=1.0, diamond_half_diagonal=0.4, core_cells=8, radial_cells=18, radial_grading=1.2)
    segments: list[Segment] = [StraightSegment('straight_1', 10.0, [0.0, 0.0, 1.0], 20, 1.0), BendSegment('bend_2', 8.0, [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], 45.0, 20, 1.15), StraightSegment('straight_3', 20.0, rotate_vec([0.0, 0.0, 1.0], [0.0, 1.0, 0.0], 45.0), 20, 1.0)]
    return (mesh, segments)

def write_geo(path: str | Path, text: str) -> None:
    clean_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith('//'):
            continue
        clean_lines.append(line)
    Path(path).write_text('\n'.join(clean_lines).rstrip() + '\n', encoding='utf-8')

def main(argv: list[str]) -> int:
    print('Генератор трубы для Gmsh v5: ромб-ядро, секторная quad-сетка, сгущение к стенке и вдоль трубы.')
    print('Без input.txt: все параметры вводятся в консоли на русском языке.\n')
    if '--пример' in argv or '--demo' in argv:
        mesh, segments = make_demo()
        output_file = 'pipe.geo'
    else:
        mesh, segments, output_file = read_user_settings()
    approx = estimate_hex_count(mesh, segments)
    if approx > 1000000:
        print('\nВнимание: расчётно получится больше 1 000 000 объёмных ячеек.')
        print('Gmsh может долго строить сетку или закрыться из-за памяти. Это не ошибка геометрии.')
        print('Для проверки лучше временно уменьшить деления поперёк или вдоль трубы.')
    text = make_geo_text(mesh, segments)
    write_geo(output_file, text)
    print(f'\nГотово: создан файл {output_file}')
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
