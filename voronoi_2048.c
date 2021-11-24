#include <stdint.h>
#include <limits.h>
#include <pthread.h>

#define ID uint16_t

void voronoi_2048_r(ID matrix[2048][2048], const int sx[], const int sy[], int n_seeds, int cx[2], int cy[2]){
 
 // get closest seed for each corner
  for(int i = 0; i<2; ++i){
          for(int j = 0; j<2; ++j){
                  int min_dist = INT_MAX;
                  for (ID seed = 0; seed<n_seeds; ++seed){
                        int curr_dist = (cx[i]-sx[seed])*(cx[i]-sx[seed]) + (cy[j]-sy[seed])*(cy[j]-sy[seed]);
                        if (min_dist > curr_dist){
                                matrix[cx[i]][cy[j]] = seed;
                                min_dist = curr_dist;
                        }
                }
          }
  }

  // check if corners are all equal
  if(   (matrix[cx[0]][cy[0]] == matrix[cx[0]][cy[1]]) &&
        (matrix[cx[0]][cy[1]] == matrix[cx[1]][cy[1]]) &&
        (matrix[cx[1]][cy[1]] == matrix[cx[1]][cy[0]]) ){
    // set all the area to the same seed ID
    for(int i = cx[0]; i<=cx[1]; ++i){
      for(int j = cy[0]; j<=cy[1]; ++j){
        matrix[i][j] = matrix[cx[0]][cy[0]];
      }
    }
  }else{
    // divide and conquer
    voronoi_2048_r(matrix, sx, sy, n_seeds, (int[2]){cx[0], (cx[0] + cx[1])/2}, (int[2]){cy[0], (cy[0] + cy[1])/2});
    voronoi_2048_r(matrix, sx, sy, n_seeds, (int[2]){cx[0], (cx[0] + cx[1])/2}, (int[2]){((cy[0] + cy[1])/2) + 1, cy[1]});
    voronoi_2048_r(matrix, sx, sy, n_seeds, (int[2]){((cx[0] + cx[1])/2) + 1, cx[1]}, (int[2]){((cy[0] + cy[1])/2) + 1, cy[1]});
    voronoi_2048_r(matrix, sx, sy, n_seeds, (int[2]){((cx[0] + cx[1])/2) + 1, cx[1]}, (int[2]){cy[0], (cy[0] + cy[1])/2});
  }

}




struct tA{
ID (*matrix)[2048];
int *sx;
int *sy;
int n_seeds;
};



void * voronoi_2048_t0(void *args){
  struct tA *a = (struct tA *) args;
  voronoi_2048_r(a->matrix, a->sx, a->sy, a->n_seeds, (int[2]){0, (2048-1)/2}, (int[2]){0, (2048-1)/2});
  return NULL;
}
void * voronoi_2048_t1(void *args){
  struct tA *a = (struct tA *) args;
  voronoi_2048_r(a->matrix, a->sx, a->sy, a->n_seeds, (int[2]){0, (2048-1)/2}, (int[2]){((2048-1)/2)+1, 2048-1});
  return NULL;
}
void * voronoi_2048_t2(void *args){
  struct tA *a = (struct tA *) args;
  voronoi_2048_r(a->matrix, a->sx, a->sy, a->n_seeds, (int[2]){((2048-1)/2)+1, 2048-1}, (int[2]){((2048-1)/2)+1, 2048-1});
  return NULL;
}
void * voronoi_2048_t3(void *args){
  struct tA *a = (struct tA *) args;
  voronoi_2048_r(a->matrix, a->sx, a->sy, a->n_seeds, (int[2]){((2048-1)/2)+1, 2048-1}, (int[2]){0, (2048-1)/2});
  return NULL;
}




void voronoi_2048(ID matrix[2048][2048], int sx[], int sy[], int n_seeds, int threaded){
  if (threaded){
    struct tA a = (struct tA){matrix, sx, sy, n_seeds};

    pthread_t t0, t1, t2, t3;

    pthread_create(&t0, NULL, voronoi_2048_t0, &a);
    pthread_create(&t1, NULL, voronoi_2048_t1, &a);
    pthread_create(&t2, NULL, voronoi_2048_t2, &a);
    pthread_create(&t3, NULL, voronoi_2048_t3, &a);

    pthread_join(t0, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);

  }else{
    voronoi_2048_r(matrix, sx, sy, n_seeds, (int[2]){0, 2048-1}, (int[2]){0, 2048-1});
  }
}

