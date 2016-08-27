#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "polygon_data.c"


int in_polygon(double x, double y, int polygon_idx){

    if (
        x < all_polygons[polygon_idx].edge->x_min ||
        x > all_polygons[polygon_idx].edge->x_max ||
        y < all_polygons[polygon_idx].edge->y_min ||
        y > all_polygons[polygon_idx].edge->y_max
    )
        return 0;

    int k;
    int c=0;
    int cnt = all_polygons[polygon_idx].el_count;
    for(k=0; k < cnt; k++){

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
        if (
            ((py <= y && y < py_prev) || (py_prev <= y && y < py)) && 
            (x > (px_prev-px) * (y-py) / (py_prev-py) + px)
        ){
            c = 1 - c;
        }
    }

    return c % 2;
}


int polygon_get_polygon_idx_collision(double x, double y)
{
    int polygons_cnt =  sizeof(all_polygons) / sizeof(all_polygons[0]);
    int polygon_idx;
    for (polygon_idx=0; polygon_idx<polygons_cnt; polygon_idx++){
        if (in_polygon(x, y, polygon_idx) == 1){
            return polygon_idx;
        }
    } 
    return 0;
}
