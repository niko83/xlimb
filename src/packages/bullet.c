#include "math.h"
#include "stdlib.h"
#include "helper.h"
#include "polygon_data.c"
#include "polygon.h"
#include "bullet.h"
 

const int CELL_STEP = 60;

double vector_angle(double x, double y){
    if (x == 0){
        if (y == 0){
            return 0;
        } else if (y > 0){
            return M_PI/2;
        } else {
            return M_PI * 3 / 2;
        }
    }
    double angle = fabs(atan(y/x));
    if(x < 0){
        if(y < 0){
            return M_PI + angle;
        } else {
            return M_PI - angle;
        }
    } else {
        if(y < 0){
            return 2 * M_PI - angle;
        } else {
            return angle;
        }
    }
}

double vector_get_angle(double x, double y){
    
    if (x == 0){
        if (y == 0){
            return 0;
        } else if (y > 0){
            return M_PI/2;
        }else{
            return M_PI * 3 / 2;
        }
    }

    double angle = fabs(atan(y / x));

    if (x < 0){
        if (y < 0){
            return M_PI + angle;
        }else{
            return M_PI - angle;
        }
    }else{
        if (y < 0){
            return 2 * M_PI - angle;
        } else {
            return angle;
        }
    }
}


int get_intersection_angle(
        double p1x, double p1y,
        double p2x, double p2y,
        int p3x, int p3y,
        int p4x, int p4y, 
        double *angle_intersection
){
    
    double x;

    double line1[2], line2[2];
    int status1 = helper_resolve_line(p1x, p1y, p2x, p2y, line1);
    int status2 = helper_resolve_line(p3x, p3y, p4x, p4y, line2);

    if (line1[0] == line2[0]){
        return 0;
    } else if (status1 == 0){
        x = (double) p1x;
    } else if (status2 == 0){
        x = (double) p3x;
    } else {
        x = (line2[1] - line1[1])/(line1[0] - line2[0]);
    }

    if ((p1x<=x && x<=p2x) || (p2x<=x && x<=p1x)) {

        double ship_angle = vector_get_angle(p2x - p1x, p2y - p1y); 

        double polygon_angle = vector_get_angle(p4x - p3x, p4y - p3y);

        if (polygon_angle >= M_PI){
            polygon_angle -= M_PI;
        }

       *angle_intersection = ship_angle - polygon_angle;
        while (*angle_intersection > M_PI/2){
            *angle_intersection -= M_PI;
        }
        return 1;
    }
    return 0;
}

int get_angle_collision(double x1, double y1, double x2, double y2, int polygon_idx, double *angle){

    int k;
    int cnt = all_polygons[polygon_idx].el_count;
    for(k=0; k< cnt; k++){

        int px = (*all_polygons[polygon_idx].mtp+k)->x;
        int py = (*all_polygons[polygon_idx].mtp+k)->y;

        int px_prev, py_prev;
        if(k==0){
            px_prev = (*all_polygons[polygon_idx].mtp+cnt-1)->x;
            py_prev = (*all_polygons[polygon_idx].mtp+cnt-1)->y; 
        }else{
            px_prev = (*all_polygons[polygon_idx].mtp+k-1)->x;
            py_prev = (*all_polygons[polygon_idx].mtp+k-1)->y; 
        }
           
        if (get_intersection_angle(x1, y1, x2, y2, px, py, px_prev, py_prev, angle)){
            return 1;
        }
    }
    return 0;

}


void bullet_calculate_position(
        double FRAME_INTERVAL,
        PyObject * obj
){

    PyObject * life_limit_py = PyObject_GetAttrString(obj, "life_limit");
    Py_DECREF(life_limit_py);
    double life_limit = PyFloat_AsDouble(life_limit_py);

    PyObject * new_life_limit = PyFloat_FromDouble(life_limit-FRAME_INTERVAL);
    PyObject_SetAttrString(obj, "life_limit", new_life_limit);
    Py_DECREF(new_life_limit);

    PyObject * prev_able_to_make = PyObject_GetAttrString(obj, "able_to_make_tracing");
    Py_DECREF(prev_able_to_make);
    double able_to_make_tracing = PyFloat_AsDouble(prev_able_to_make);
    if (able_to_make_tracing > -100){
        PyObject * new_able_to_make = PyFloat_FromDouble(able_to_make_tracing+FRAME_INTERVAL);
        PyObject_SetAttrString(obj, "able_to_make_tracing", new_able_to_make);
        Py_DECREF(new_able_to_make);
    }

    PyObject * current_speed = PyObject_GetAttrString(obj, "current_speed");
    Py_DECREF(current_speed);

    PyObject * current_speed_x_py =  PyObject_GetAttrString(current_speed, "x");
    Py_DECREF(current_speed_x_py);
    PyObject * current_speed_y_py =  PyObject_GetAttrString(current_speed, "y");
    Py_DECREF(current_speed_y_py);

    double current_speed_x = PyFloat_AsDouble(current_speed_x_py);
    double current_speed_y = PyFloat_AsDouble(current_speed_y_py);
    if (current_speed_x == 0 && current_speed_y == 0){
        return;
    }

    PyObject * current_position = PyObject_GetAttrString(obj, "current_position");
    Py_DECREF(current_position);

    PyObject * cpx_py = PyObject_GetAttrString(current_position, "x");
    Py_DECREF(cpx_py);
    double cpx = PyFloat_AsDouble(cpx_py);
    PyObject * cpy_py = PyObject_GetAttrString(current_position, "y");
    Py_DECREF(cpy_py);
    double cpy = PyFloat_AsDouble(cpy_py);

    double candidat_position_x = cpx + current_speed_x * FRAME_INTERVAL;
    double candidat_position_y = cpy - current_speed_y * FRAME_INTERVAL;

    int approx_x = floor(candidat_position_x/CELL_STEP);
    int approx_y = floor(candidat_position_y/CELL_STEP);

    PyObject * approx_x_py = PyLong_FromLong(approx_x);
    PyObject * approx_y_py = PyLong_FromLong(approx_y);
    Py_DECREF(PyObject_GetAttrString(obj, "approx_x"));
    Py_DECREF(PyObject_GetAttrString(obj, "approx_y"));
    PyObject_SetAttrString(obj, "approx_x", approx_x_py);
    PyObject_SetAttrString(obj, "approx_y", approx_y_py);
    Py_DECREF(approx_x_py);
    Py_DECREF(approx_y_py);

    int polygon_idx = 0;
    if (
            approx_x < sizeof(polygon_cell)/sizeof(polygon_cell[0]) && 
            approx_y < sizeof(polygon_cell[0])/sizeof(polygon_cell[0][0])
    ){
        if (polygon_cell[approx_x][approx_y] == 1){
            polygon_idx = polygon_get_polygon_idx_collision(candidat_position_x, candidat_position_y);
        }
    } else {
        // fallback IndexError
        PyObject * zero_x = PyLong_FromLong(0);
        PyObject * zero_y = PyLong_FromLong(0);
        Py_DECREF(PyObject_GetAttrString(obj, "approx_x"));
        Py_DECREF(PyObject_GetAttrString(obj, "approx_y"));
        PyObject_SetAttrString(obj, "approx_x", zero_x);
        PyObject_SetAttrString(obj, "approx_y", zero_y);
        Py_DECREF(zero_x);
        Py_DECREF(zero_y);
    }

    PyObject * ricochet_py = PyObject_GetAttrString(obj, "ricochet");
    Py_DECREF(ricochet_py);
    int ricochet = PyLong_AsLong(ricochet_py);

    if (polygon_idx && ricochet==0){
        PyObject * minus_py = PyFloat_FromDouble(-1);
        PyObject_SetAttrString(obj, "life_limit", minus_py);
        Py_DECREF(minus_py);
        return;
    }

    double angle;
    if (polygon_idx && ricochet==1){
        if (get_angle_collision(cpx, cpy, candidat_position_x, candidat_position_y, polygon_idx, &angle)){
            angle=angle*2 + vector_angle(current_speed_x, current_speed_y);
            double length = sqrt(pow(current_speed_x, 2) + pow(current_speed_y, 2));
            PyObject * c_speed_x_py = PyFloat_FromDouble(cos(angle) * length);
            PyObject * c_speed_y_py = PyFloat_FromDouble(sin(angle) * length);
            PyObject_SetAttrString(current_speed, "x", c_speed_x_py);
            PyObject_SetAttrString(current_speed, "y", c_speed_y_py);
            Py_DECREF(c_speed_x_py);
            Py_DECREF(c_speed_y_py);
        }else{
            PyObject * minus_py = PyFloat_FromDouble(-1);
            PyObject_SetAttrString(obj, "life_limit", minus_py);
            Py_DECREF(minus_py);
        }
    }

    PyObject * candidat_position_x_py = PyFloat_FromDouble(candidat_position_x);
    PyObject * candidat_position_y_py = PyFloat_FromDouble(candidat_position_y);
    PyObject_SetAttrString(current_position, "x", candidat_position_x_py);
    PyObject_SetAttrString(current_position, "y", candidat_position_y_py);
    Py_DECREF(candidat_position_x_py);
    Py_DECREF(candidat_position_y_py);

    return;
}
