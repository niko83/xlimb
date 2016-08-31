#include "math.h"
#include "stdlib.h"
#include "helper.h"
#include "polygon_data.c"
#include "polygon_data.h"
#include "polygon.h"
#include "bullet.h"
 

const int CELL_STEP = 60;

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

    double angle = abs(atan(y / x));

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


int get_intersection_angle(int p1x, int p1y, int p2x, int p2y, int p3x, int p3y, int p4x, int p4y, double *angle_intersection){
    
    double x;

    double line1[2], line2[2];
    helper_resolve_line(p1x, p1y, p2x, p2y, line1);
    helper_resolve_line(p3x, p3y, p4x, p4y, line2);

    if (line1[0] == line2[0]){
        return 0;
    } else if (line1[0] == 0 && line1[1] == 0){
        x = (double) p1x;
    } else if (line2[0] == 0 && line2[1]==0){
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

int get_angle_collision(double x1, double y1, double x2, double y2, int polygon_idx, double *result){

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
           
        double result;
        if (get_intersection_angle(x1, y1, x2, y2, px, py, px_prev, py_prev, &result) == 1){
            return 1;
        }
    }
    return 0;

}


void bullet_calculate_position(
        double FRAME_INTERVAL,
        PyObject * obj
){
    double life_limit = PyFloat_AsDouble(PyObject_GetAttrString(obj, "life_limit"));

    if (life_limit < FRAME_INTERVAL){
        PyObject_SetAttrString(obj, "life_limit", PyFloat_FromDouble(-1));
        return;
    }
    PyObject_SetAttrString(obj, "life_limit", PyFloat_FromDouble(life_limit-FRAME_INTERVAL));

    double able_to_make_tracing = PyFloat_AsDouble(PyObject_GetAttrString(obj, "able_to_make_tracing"));
    if (able_to_make_tracing > -100){
        PyObject_SetAttrString(obj, "able_to_make_tracing", PyFloat_FromDouble(able_to_make_tracing+FRAME_INTERVAL));
    }

    PyObject * current_speed = PyObject_GetAttrString(obj, "current_speed");

    double current_speed_x = PyFloat_AsDouble(PyObject_GetAttrString(current_speed, "x"));
    double current_speed_y = PyFloat_AsDouble(PyObject_GetAttrString(current_speed, "y"));
    if (current_speed_x == 0 && current_speed_y == 0){
        return;
    }

    PyObject * current_position = PyObject_GetAttrString(obj, "current_position");
    double current_position_x = PyFloat_AsDouble(PyObject_GetAttrString(current_position, "x"));
    double current_position_y = PyFloat_AsDouble(PyObject_GetAttrString(current_position, "y"));

    double candidat_position_x = current_position_x + current_speed_x * FRAME_INTERVAL;
    double candidat_position_y = current_position_y - current_speed_y * FRAME_INTERVAL;

    int approx_x = floor(candidat_position_x/CELL_STEP);
    int approx_y = floor(candidat_position_y/CELL_STEP);

    PyObject_SetAttrString(obj, "approx_x", PyLong_FromLong(approx_x));
    PyObject_SetAttrString(obj, "approx_y", PyLong_FromLong(approx_y));

    int polygon_idx = 0;
    if (approx_x < 100000 && approx_y < 100000){
        if (polygon_cell[approx_x][approx_y] == 1){
            polygon_idx = polygon_get_polygon_idx_collision(candidat_position_x, candidat_position_y);
        }
    } else {
        // fallback IndexError
        PyObject_SetAttrString(obj, "approx_x", PyLong_FromLong(0));
        PyObject_SetAttrString(obj, "approx_y", PyLong_FromLong(0));
    }

    int ricochet = PyLong_AsLong(PyObject_GetAttrString(obj, "ricochet"));
    if (polygon_idx && ricochet==0){
        PyObject_SetAttrString(obj, "life_limit", PyFloat_FromDouble(-1));
        return;
    }

    double angle;
    if (polygon_idx && ricochet==1){
        if (get_angle_collision(current_position_x, current_position_y, candidat_position_x, candidat_position_y, polygon_idx, &angle) == 1){
            /* length=self.current_speed.length, */
            /* angle=angle*2 + self.current_speed.angle() */
            PyObject_SetAttrString(current_speed, "x", PyFloat_FromDouble(400));
            PyObject_SetAttrString(current_speed, "y", PyFloat_FromDouble(400));
        }else{
            PyObject_SetAttrString(obj, "life_limit", PyFloat_FromDouble(-1));
        }
    }

    PyObject_SetAttrString(current_position, "x", PyFloat_FromDouble(candidat_position_x));
    PyObject_SetAttrString(current_position, "y", PyFloat_FromDouble(candidat_position_y));
    return;
}