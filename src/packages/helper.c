#include "math.h"
#include <stdio.h>


double helper_distance(double x1, double y1, double x2, double y2) 
{
    return sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2));
}


double * helper_resolve_line(double x1, double y1, double x2, double y2, double* KB_result)
{
    double K, B;
    if (x1 == x2){ /* vertical */
        K = 0; B = 0;
    } else {
        K = (y2 - y1) / (x2 - x1);
        B = y2 - K * x2;
    }

    KB_result[0] = K;
    KB_result[1] = B;
    return KB_result;
}
