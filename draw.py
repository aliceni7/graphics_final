from display import *
from matrix import *
from gmath import *

def draw_scanline(x0, z0, x1, z1, y, screen, zbuffer, color):
    if x0 > x1:
        tx = x0
        tz = z0
        x0 = x1
        z0 = z1
        x1 = tx
        z1 = tz

    x = x0
    z = z0
    delta_z = (z1 - z0) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0

    while x <= x1:
        plot(screen, zbuffer, color, x, y, z)
        x+= 1
        z+= delta_z

def scanline_convert(polygons, i, screen, zbuffer, color):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
               (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
               (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]

    points.sort(key = lambda x: x[1])
    x0 = points[BOT][0]
    z0 = points[BOT][2]
    x1 = points[BOT][0]
    z1 = points[BOT][2]
    y = int(points[BOT][1])

    distance0 = int(points[TOP][1]) - y * 1.0 + 1
    distance1 = int(points[MID][1]) - y * 1.0 + 1
    distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

    dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

    while y <= int(points[TOP][1]):
        if ( not flip and y >= int(points[MID][1])):
            flip = True

            dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
            dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
            x1 = points[MID][0]
            z1 = points[MID][2]

        #draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
        draw_scanline(int(x0), z0, int(x1), z1, y, screen, zbuffer, color)
        x0+= dx0
        z0+= dz0
        x1+= dx1
        z1+= dz1
        y+= 1



def add_polygon( polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2 ):
    add_point(polygons, x0, y0, z0)
    add_point(polygons, x1, y1, z1)
    add_point(polygons, x2, y2, z2)
    # print([x0, y0, z0])
    # print([x1, y1, z1])
    # print([x2, y2, z2])
    # print()

def draw_polygons( polygons, screen, zbuffer, view, ambient, light, symbols, reflect):
    if len(polygons) < 2:
        print('Need at least 3 points to draw')
        return

    point = 0
    while point < len(polygons) - 2:

        normal = calculate_normal(polygons, point)[:]
        if normal[2] > 0:

            color = get_lighting(normal, view, ambient, light, symbols, reflect )
            scanline_convert(polygons, point, screen, zbuffer, color)

        point+= 3

def add_cone( polygons, x, y, z, radius, height, step):
    circle = generate_horiz_circle(x, y, z, radius, step)
    top = [x, y + height, z]

    i = 0
    while i < len(circle) - 1:
        p0 = circle[i]
        p1 = circle[i + 1]
        add_polygon(polygons, p0[0], p0[1], p0[2], p1[0], p1[1], p1[2], top[0], top[1], top[2])
        add_polygon(polygons, p0[0], p0[1], p0[2], x, y, z, p1[0], p1[1], p1[2])

        i += 1

    p0 = circle[len(circle)-1]
    p1 = circle[0]
    add_polygon(polygons, p0[0], p0[1], p0[2], p1[0], p1[1], p1[2], top[0], top[1], top[2])
    add_polygon(polygons, p0[0], p0[1], p0[2], x, y, z, p1[0], p1[1], p1[2])

def add_hollow_cone( polygons, x, y, z, radius, height, thickness, step):
    outer = generate_horiz_circle(x, y, z, radius, step)
    inner = generate_horiz_circle(x, y, z, radius - thickness, step)

    to = [x, y + height, z]
    ti = [x, y + height - thickness, z]

    i = 0
    while i < len(outer) - 1:
        o0 = outer[i]
        o1 = outer[i + 1]
        i0 = inner[i]
        i1 = inner[i + 1]

        #outer
        add_polygon( polygons, o0[0], o0[1], o0[2], o1[0], o1[1], o1[2], to[0], to[1], to[2])

        #inner
        add_polygon( polygons, i1[0], i1[1], i1[2], i0[0], i0[1], i0[2], ti[0], ti[1], ti[2])

        #edge
        add_polygon( polygons, o0[0], o0[1], o0[2], i0[0], i0[1], i0[2], o1[0], o1[1], o1[2])
        add_polygon( polygons, i0[0], i0[1], i0[2], i1[0], i1[1], i1[2], o1[0], o1[1], o1[2])
        i += 1

    o0 = outer[-1]
    o1 = outer[0]
    i0 = inner[-1]
    i1 = inner[0]

    #outer
    add_polygon( polygons, o0[0], o0[1], o0[2], o1[0], o1[1], o1[2], to[0], to[1], to[2])

    #inner
    add_polygon( polygons, i1[0], i1[1], i1[2], i0[0], i0[1], i0[2], ti[0], ti[1], ti[2])

    #edge
    add_polygon( polygons, o0[0], o0[1], o0[2], i0[0], i0[1], i0[2], o1[0], o1[1], o1[2])
    add_polygon( polygons, i0[0], i0[1], i0[2], i1[0], i1[1], i1[2], o1[0], o1[1], o1[2])




def add_cylinder( polygons, x, y, z, radius, height, step):
    bottom = generate_horiz_circle(x, y, z, radius, step)

    cbot = [x, y, z]
    ctop = [x, y + height, z]

    i = 0
    while i < len(bottom) - 1:
        b0 = bottom[i]
        b1 = bottom[i + 1]
        add_polygon(polygons, b0[0], b0[1], b0[2], b1[0], b1[1], b1[2], b0[0], b0[1] + height, b0[2])
        add_polygon(polygons, b0[0], b0[1] + height, b0[2], b1[0], b1[1], b1[2], b1[0], b1[1] + height, b1[2] )
        add_polygon(polygons, b0[0], b0[1], b0[2],  cbot[0], cbot[1], cbot[2], b1[0], b1[1], b1[2])
        add_polygon(polygons, b0[0], b0[1] + height, b0[2], b1[0], b1[1] + height, b1[2], ctop[0], ctop[1], ctop[2])


        i += 1

    b0 = bottom[len(bottom) - 1]
    b1 = bottom[0]
    add_polygon(polygons, b0[0], b0[1], b0[2], b1[0], b1[1], b1[2], b0[0], b0[1] + height, b0[2])
    add_polygon(polygons, b0[0], b0[1] + height, b0[2], b1[0], b1[1], b1[2], b1[0], b1[1] + height, b1[2])
    add_polygon(polygons, b0[0], b0[1], b0[2],  cbot[0], cbot[1], cbot[2], b1[0], b1[1], b1[2])
    add_polygon(polygons, b0[0], b0[1] + height, b0[2], b1[0], b1[1] + height, b1[2], ctop[0], ctop[1], ctop[2])

def add_hollow_cylinder( polygons, x, y, z, radius, height, thickness, step ):
    bottom_outer = generate_horiz_circle( x, y, z, radius, step)
    bottom_inner = generate_horiz_circle( x, y, z, radius - thickness, step)

    cbot = [x, y, z]
    ctop = [x, y + height, z]

    i = 0
    while i < len(bottom_outer) - 1:
        bo0 = bottom_outer[i] #bottom outer 0
        bo1 = bottom_outer[i + 1] #bottom outer 1
        bi0 = bottom_inner[i] #bottom inner 0
        bi1 = bottom_inner[i + 1] #bottom inner 1

        to0 = [bo0[0], bo0[1] + height, bo0[2]] #top outer 0
        to1 = [bo1[0], bo1[1] + height, bo1[2]] #top outer 1
        ti0 = [bi0[0], bi0[1] + height, bi0[2]] #top inner 0
        ti1 = [bi1[0], bi1[1] + height, bi1[2]] #top inner 1

        #outside
<<<<<<< HEAD
        add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], to1[0], to1[1], to1[2])
        add_polygon( polygons, to0[0], to0[1], to0[2], bo0[0], bo0[1], bo0[2], to1[0], to1[1], to1[2])

        #inside
        add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2])
        add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti1[0], ti1[1], ti1[2], bi1[0], bi1[1], bi1[2])

        #edges
        add_polygon( polygons, bo0[0], bo0[1], bo0[2], bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2])
        add_polygon( polygons, bi1[0], bi1[1], bi1[2], bo1[0], bo1[1], bo1[2], bo0[0], bo0[1], bo0[2])

        add_polygon( polygons, ti1[0], ti1[1], ti1[2], to0[0], to0[1], to0[2], to1[0], to1[1], to1[2])
        add_polygon( polygons, ti0[0], ti0[1], ti0[2], to0[0], to0[1], to0[2], ti1[0], ti1[1], ti1[2])
=======
        add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], to0[0], to0[1], to0[2])
        #add_polygon( polygons, to0[0], to0[1], to0[2], bo1[0], bo1[1], bo1[2], to1[0], to1[1], to1[2])
        add_polygon( polygons, to0[0], to0[1], to0[2], to1[0], to1[1], to1[2], bo1[0], bo1[1], bo1[2])
        
        #inside
        #add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti0[0], ti0[1], ti0[2], bi1[0], bi1[1], bi1[2])
        add_polygon( polygons, bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2], ti0[0], ti0[1], ti0[2])
        add_polygon( polygons, ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2], bi1[0], bi1[1], bi1[2])

        #edges
        #add_polygon( polygons, bo0[0], bo0[1], bo0[2], bi0[0], bi0[1], bi0[2], bo1[0], bo1[1], bo1[2])
        add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], bi0[0], bi0[1], bi0[2])
        add_polygon( polygons, bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2], bo1[0], bo1[1], bo1[2])

        add_polygon( polygons, to0[0], to0[1], to0[2], to1[0], to1[1], to1[2], ti0[0], ti0[1], ti0[2])
        #add_polygon( polygons, ti0[0], ti0[1], ti0[2], to1[0], to1[1], to1[2], ti1[0], ti1[1], ti1[2])
        add_polygon( polygons, ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2], to1[0], to1[1], to1[2])
>>>>>>> 770552e4b9f5ef4868b4e306a3e7d25c66ff89e0
        i += 1

    bo0 = bottom_outer[-1] #bottom outer 0
    bo1 = bottom_outer[0] #bottom outer 1
    bi0 = bottom_inner[-1] #bottom inner 0
    bi1 = bottom_inner[0] #bottom inner 1

    to0 = [bo0[0], bo0[1] + height, bo0[2]] #top outer 0
    to1 = [bo1[0], bo1[1] + height, bo1[2]] #top outer 1
    ti0 = [bi0[0], bi0[1] + height, bi0[2]] #top inner 0
    ti1 = [bi1[0], bi1[1] + height, bi1[2]] #top inner 1

    #outside
<<<<<<< HEAD
    add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], to1[0], to1[1], to1[2])
    add_polygon( polygons, to0[0], to0[1], to0[2], bo0[0], bo0[1], bo0[2], to1[0], to1[1], to1[2])

    #inside
    add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2])
    add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti1[0], ti1[1], ti1[2], bi1[0], bi1[1], bi1[2])

    #edges
    add_polygon( polygons, bo0[0], bo0[1], bo0[2], bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2])
    add_polygon( polygons, bi1[0], bi1[1], bi1[2], bo1[0], bo1[1], bo1[2], bo0[0], bo0[1], bo0[2])

    add_polygon( polygons, ti1[0], ti1[1], ti1[2], to0[0], to0[1], to0[2], to1[0], to1[1], to1[2])
    add_polygon( polygons, ti0[0], ti0[1], ti0[2], to0[0], to0[1], to0[2], ti1[0], ti1[1], ti1[2])
=======
    add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], to0[0], to0[1], to0[2])
    #add_polygon( polygons, to0[0], to0[1], to0[2], bo1[0], bo1[1], bo1[2], to1[0], to1[1], to1[2])
    add_polygon( polygons, to0[0], to0[1], to0[2], to1[0], to1[1], to1[2], bo1[0], bo1[1], bo1[2])

    #inside
    #add_polygon( polygons, bi0[0], bi0[1], bi0[2], ti0[0], ti0[1], ti0[2], bi1[0], bi1[1], bi1[2])
    add_polygon( polygons, bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2], ti0[0], ti0[1], ti0[2])
    add_polygon( polygons, ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2], bi1[0], bi1[1], bi1[2])

    #edges
    #add_polygon( polygons, bo0[0], bo0[1], bo0[2], bi0[0], bi0[1], bi0[2], bo1[0], bo1[1], bo1[2])
    add_polygon( polygons, bo0[0], bo0[1], bo0[2], bo1[0], bo1[1], bo1[2], bi0[0], bi0[1], bi0[2])
    add_polygon( polygons, bi0[0], bi0[1], bi0[2], bi1[0], bi1[1], bi1[2], bo1[0], bo1[1], bo1[2])

    add_polygon( polygons, to0[0], to0[1], to0[2], to1[0], to1[1], to1[2], ti0[0], ti0[1], ti0[2])
    #add_polygon( polygons, ti0[0], ti0[1], ti0[2], to1[0], to1[1], to1[2], ti1[0], ti1[1], ti1[2])
    add_polygon( polygons, ti0[0], ti0[1], ti0[2], ti1[0], ti1[1], ti1[2], to1[0], to1[1], to1[2])
>>>>>>> 770552e4b9f5ef4868b4e306a3e7d25c66ff89e0


def add_box( polygons, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z)
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z)

    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1)
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1)

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1)
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1)

    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z)
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z)

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1)
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z)
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z)
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1)

def add_sphere(polygons, cx, cy, cz, r, step ):
    points = generate_sphere(cx, cy, cz, r, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    step+= 1
    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt
            p1 = p0+1
            p2 = (p1+step) % (step * (step-1))
            p3 = (p0+step) % (step * (step-1))

            if longt != step - 2:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p1][0],
                             points[p1][1],
                             points[p1][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2])
            if longt != 0:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2],
                             points[p3][0],
                             points[p3][1],
                             points[p3][2])


def generate_sphere( cx, cy, cz, r, step ):
    points = []

    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop+1):
            circ = circle/float(step)

            x = r * math.cos(math.pi * circ) + cx
            y = r * math.sin(math.pi * circ) * math.cos(2*math.pi * rot) + cy
            z = r * math.sin(math.pi * circ) * math.sin(2*math.pi * rot) + cz

            points.append([x, y, z])
            #print 'rotation: %d\tcircle%d'%(rotation, circle)
    return points

def add_torus(polygons, cx, cy, cz, r0, r1, step ):
    points = generate_torus(cx, cy, cz, r0, r1, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt;
            if (longt == (step - 1)):
                p1 = p0 - longt;
            else:
                p1 = p0 + 1;
            p2 = (p1 + step) % (step * step);
            p3 = (p0 + step) % (step * step);

            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p3][0],
                        points[p3][1],
                        points[p3][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2] )
            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2],
                        points[p1][0],
                        points[p1][1],
                        points[p1][2] )


def generate_torus( cx, cy, cz, r0, r1, step ):
    points = []
    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop):
            circ = circle/float(step)

            x = math.cos(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cx;
            y = r0 * math.sin(2*math.pi * circ) + cy;
            z = -1*math.sin(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cz;

            points.append( [x, y, z] )
    return points

def generate_horiz_circle(x, y, z, r, step ):
    points = []
    x0 = r + x
    y0 = y
    z0 = z
    i = 1

    points.append([x0, y0, z0])

    while i <= step:
        t = float(i)/step
        x1 = r * math.cos(2*math.pi * t) + x;
        z1 = r * math.sin(2*math.pi * t) + z;
        points.append([x1, y0, z1])
        i+= 1

    return points

def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy
    i = 1

    while i <= step:
        t = float(i)/step
        x1 = r * math.cos(2*math.pi * t) + cx;
        y1 = r * math.sin(2*math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        i+= 1

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):

    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    i = 1
    while i <= step:
        t = float(i)/step
        x = t * (t * (xcoefs[0] * t + xcoefs[1]) + xcoefs[2]) + xcoefs[3]
        y = t * (t * (ycoefs[0] * t + ycoefs[1]) + ycoefs[2]) + ycoefs[3]
        #x = xcoefs[0] * t*t*t + xcoefs[1] * t*t + xcoefs[2] * t + xcoefs[3]
        #y = ycoefs[0] * t*t*t + ycoefs[1] * t*t + ycoefs[2] * t + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        i+= 1


def draw_lines( matrix, screen, zbuffer, color ):
    if len(matrix) < 2:
        print('Need at least 2 points to draw')
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line( int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )



def draw_line( x0, y0, z0, x1, y1, z1, screen, zbuffer, color ):

    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x + 1
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y) + 1
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0

    while ( loop_start < loop_end ):
        plot( screen, zbuffer, color, x, y, z )
        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):

            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east
        z+= dz
        loop_start+= 1
    plot( screen, zbuffer, color, x, y, z )
