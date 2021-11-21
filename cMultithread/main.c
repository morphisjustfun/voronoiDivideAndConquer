#include <math.h>
#include <memory.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

static int threadsNumber = 1;

struct Seed {
  int x;
  int y;
};

struct VoronoiDiagram {
  int n;
  int seedsCount;
  struct Seed **seeds;
  int **matrix;
  int counterThread;
};

struct VoronoiArguments {
  struct VoronoiDiagram *diagram;
  int **corners;
  int threadCounter;
};

struct VoronoiDiagram *constructorVoronoiDiagram(int n, struct Seed **seeds,
                                                 int seedsCount) {
  struct VoronoiDiagram *voronoiDiagram =
      (struct VoronoiDiagram *)malloc(sizeof(struct VoronoiDiagram));
  voronoiDiagram->n = n;
  voronoiDiagram->seedsCount = seedsCount;
  voronoiDiagram->counterThread = 1;

  voronoiDiagram->seeds =
      (struct Seed **)malloc(sizeof(struct Seed *) * seedsCount);
  for (int i = 0; i < seedsCount; i++) {
    voronoiDiagram->seeds[i] = seeds[i];
  }

  voronoiDiagram->matrix = (int **)malloc(n * sizeof(int *));

  for (int i = 0; i < n; i++) {
    voronoiDiagram->matrix[i] = (int *)malloc(n * sizeof(int));
    /* memset(voronoiDiagram->matrix[i], 0, n * sizeof(int)); */
    for (int j = 0; j < n; j++) {
      voronoiDiagram->matrix[i][j] = -1;
    }
  }

  for (int i = 0; i < seedsCount; i++) {
    voronoiDiagram->matrix[seeds[i]->x][seeds[i]->y] = i;
  }

  return voronoiDiagram;
}

double distance(struct Seed *seed, int x, int y) {
  return sqrt(pow(seed->x - x, 2) + pow(seed->y - y, 2));
}

/* void clearVoronoiDiagram(struct VoronoiDiagram *voronoiDiagram) { */
/*   for (int i = 0; i < voronoiDiagram->n; i++) { */
/*     for (int j = 0; j < voronoiDiagram->n; j++) { */
/*       voronoiDiagram->matrix[i][j] = -1; */
/*     } */
/*   } */

/*   for (int i = 0; i < voronoiDiagram->seedsCount; i++) { */
/*     voronoiDiagram */
/*         ->matrix[voronoiDiagram->seeds[i]->x][voronoiDiagram->seeds[i]->y] = */
/*         voronoiDiagram->seeds[i]->id; */
/*   } */
/* } */

void getDiagramHelperNonThreaded(int **corners,
                                 struct VoronoiDiagram *voronoiDiagram) {
  int countCorners = 4;

  struct Seed **closestSeeds =
      (struct Seed **)malloc(countCorners * sizeof(struct Seed *));

  int closestSeedsPositions[4];

  for (int i = 0; i < countCorners; i++) {
    // get closest seed for each corner
    closestSeeds[i] = voronoiDiagram->seeds[0];
    for (int j = 0; j < voronoiDiagram->seedsCount; j++) {
      if (distance(voronoiDiagram->seeds[j], corners[i][0], corners[i][1]) <
          distance(closestSeeds[i], corners[i][0], corners[i][1])) {
        closestSeeds[i] = voronoiDiagram->seeds[j];
        closestSeedsPositions[i] = j;
      }
    }
  }

  // check if closesSeeds are all equal
  int equal = 1;
  for (int i = 1; i < countCorners; i++) {
    if (closestSeeds[i] != closestSeeds[i - 1]) {
      equal = 0;
    }
  }

  if (equal == 1) {
    int *firstCorner = corners[0];
    int *secondCorner = corners[1];
    int *thirdCorner = corners[2];
    for (int height = firstCorner[0]; height < secondCorner[0] + 1; height++) {
      for (int width = firstCorner[1]; width < thirdCorner[1] + 1; width++) {
        voronoiDiagram->matrix[height][width] = closestSeedsPositions[0];
      }
    }
  } else {
    int **firstQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      firstQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **secondQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      secondQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **thirdQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      thirdQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **fourthQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      fourthQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }
    // firstQuadrant

    firstQuadrantCorners[0][0] = corners[0][0];
    firstQuadrantCorners[0][1] = corners[0][1];

    firstQuadrantCorners[1][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    firstQuadrantCorners[1][1] = corners[0][1];

    firstQuadrantCorners[2][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    firstQuadrantCorners[2][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2;

    firstQuadrantCorners[3][0] = corners[0][0];
    firstQuadrantCorners[3][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2;

    // secondQuadrant
    secondQuadrantCorners[0][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    secondQuadrantCorners[0][1] = corners[0][1];

    secondQuadrantCorners[1][0] = corners[1][0];
    secondQuadrantCorners[1][1] = corners[1][1];

    secondQuadrantCorners[2][0] = corners[1][0];
    secondQuadrantCorners[2][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2;

    secondQuadrantCorners[3][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    secondQuadrantCorners[3][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2;

    // thirdQuadrant
    thirdQuadrantCorners[0][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    thirdQuadrantCorners[0][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    thirdQuadrantCorners[1][0] = corners[1][0];
    thirdQuadrantCorners[1][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2 + 1;

    thirdQuadrantCorners[2][0] = corners[2][0];
    thirdQuadrantCorners[2][1] = corners[2][1];

    thirdQuadrantCorners[3][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    thirdQuadrantCorners[3][1] = corners[2][1];

    // fourthQuadrant
    fourthQuadrantCorners[0][0] = corners[0][0];
    fourthQuadrantCorners[0][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    fourthQuadrantCorners[1][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    fourthQuadrantCorners[1][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    fourthQuadrantCorners[2][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    fourthQuadrantCorners[2][1] = corners[2][1];

    fourthQuadrantCorners[3][0] = corners[3][0];
    fourthQuadrantCorners[3][1] = corners[3][1];

    getDiagramHelperNonThreaded(firstQuadrantCorners, voronoiDiagram);
    getDiagramHelperNonThreaded(secondQuadrantCorners, voronoiDiagram);
    getDiagramHelperNonThreaded(thirdQuadrantCorners, voronoiDiagram);
    getDiagramHelperNonThreaded(fourthQuadrantCorners, voronoiDiagram);

    // free
    for (int i = 0; i < 4; i++) {
      free(firstQuadrantCorners[i]);
      free(secondQuadrantCorners[i]);
      free(thirdQuadrantCorners[i]);
      free(fourthQuadrantCorners[i]);
    }

    free(firstQuadrantCorners);
    free(secondQuadrantCorners);
    free(thirdQuadrantCorners);
    free(fourthQuadrantCorners);
  }
}

void *getDiagramHelperThreaded(void *context) {
  struct VoronoiArguments *args = (struct VoronoiArguments *)context;
  struct VoronoiDiagram *voronoiDiagram = args->diagram;
  int threadCounter = args->threadCounter;
  int **corners = args->corners;
  int closestSeedsPositions[4];

  int countCorners = 4;

  struct Seed **closestSeeds =
      (struct Seed **)malloc(countCorners * sizeof(struct Seed *));

  for (int i = 0; i < countCorners; i++) {
    // get closest seed for each corner
    closestSeeds[i] = voronoiDiagram->seeds[0];
    for (int j = 0; j < voronoiDiagram->seedsCount; j++) {
      if (distance(voronoiDiagram->seeds[j], corners[i][0], corners[i][1]) <
          distance(closestSeeds[i], corners[i][0], corners[i][1])) {
        closestSeeds[i] = voronoiDiagram->seeds[j];
        closestSeedsPositions[i] = j;
      }
    }
  }

  // check if closesSeeds are all equal
  int equal = 1;
  for (int i = 1; i < countCorners; i++) {
    if (closestSeeds[i] != closestSeeds[i - 1]) {
      equal = 0;
    }
  }

  if (equal == 1) {
    int *firstCorner = corners[0];
    int *secondCorner = corners[1];
    int *thirdCorner = corners[2];
    for (int height = firstCorner[0]; height < secondCorner[0] + 1; height++) {
      for (int width = firstCorner[1]; width < thirdCorner[1] + 1; width++) {
        voronoiDiagram->matrix[height][width] = closestSeedsPositions[0];
      }
    }
  } else {
    int **firstQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      firstQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **secondQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      secondQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **thirdQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      thirdQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }

    int **fourthQuadrantCorners = (int **)malloc(4 * sizeof(int *));
    for (int i = 0; i < 4; i++) {
      fourthQuadrantCorners[i] = (int *)malloc(2 * sizeof(int));
    }
    // firstQuadrant

    firstQuadrantCorners[0][0] = corners[0][0];
    firstQuadrantCorners[0][1] = corners[0][1];

    firstQuadrantCorners[1][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    firstQuadrantCorners[1][1] = corners[0][1];

    firstQuadrantCorners[2][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    firstQuadrantCorners[2][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2;

    firstQuadrantCorners[3][0] = corners[0][0];
    firstQuadrantCorners[3][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2;

    // secondQuadrant
    secondQuadrantCorners[0][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    secondQuadrantCorners[0][1] = corners[0][1];

    secondQuadrantCorners[1][0] = corners[1][0];
    secondQuadrantCorners[1][1] = corners[1][1];

    secondQuadrantCorners[2][0] = corners[1][0];
    secondQuadrantCorners[2][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2;

    secondQuadrantCorners[3][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    secondQuadrantCorners[3][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2;

    // thirdQuadrant
    thirdQuadrantCorners[0][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    thirdQuadrantCorners[0][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    thirdQuadrantCorners[1][0] = corners[1][0];
    thirdQuadrantCorners[1][1] =
        corners[1][1] + (corners[2][1] - corners[1][1]) / 2 + 1;

    thirdQuadrantCorners[2][0] = corners[2][0];
    thirdQuadrantCorners[2][1] = corners[2][1];

    thirdQuadrantCorners[3][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2 + 1;
    thirdQuadrantCorners[3][1] = corners[2][1];

    // fourthQuadrant
    fourthQuadrantCorners[0][0] = corners[0][0];
    fourthQuadrantCorners[0][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    fourthQuadrantCorners[1][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    fourthQuadrantCorners[1][1] =
        corners[0][1] + (corners[2][1] - corners[0][1]) / 2 + 1;

    fourthQuadrantCorners[2][0] =
        corners[0][0] + (corners[1][0] - corners[0][0]) / 2;
    fourthQuadrantCorners[2][1] = corners[2][1];

    fourthQuadrantCorners[3][0] = corners[3][0];
    fourthQuadrantCorners[3][1] = corners[3][1];

    struct VoronoiArguments *args1 =
        (struct VoronoiArguments *)malloc(sizeof(struct VoronoiArguments));
    args1->diagram = voronoiDiagram;
    args1->corners = firstQuadrantCorners;
    args1->threadCounter = threadCounter + 1;

    struct VoronoiArguments *args2 =
        (struct VoronoiArguments *)malloc(sizeof(struct VoronoiArguments));
    args2->diagram = voronoiDiagram;
    args2->corners = secondQuadrantCorners;
    args2->threadCounter = threadCounter + 1;

    struct VoronoiArguments *args3 =
        (struct VoronoiArguments *)malloc(sizeof(struct VoronoiArguments));
    args3->diagram = voronoiDiagram;
    args3->corners = thirdQuadrantCorners;
    args3->threadCounter = threadCounter + 1;

    struct VoronoiArguments *args4 =
        (struct VoronoiArguments *)malloc(sizeof(struct VoronoiArguments));
    args4->diagram = voronoiDiagram;
    args4->corners = fourthQuadrantCorners;
    args4->threadCounter = threadCounter + 1;

    if (threadCounter <= threadsNumber) {
      voronoiDiagram->counterThread++;
      pthread_t thread_1;
      pthread_t thread_2;
      pthread_t thread_3;
      pthread_t thread_4;

      pthread_create(&thread_1, NULL, getDiagramHelperThreaded, (void *)args1);
      pthread_create(&thread_2, NULL, getDiagramHelperThreaded, (void *)args2);
      pthread_create(&thread_3, NULL, getDiagramHelperThreaded, (void *)args3);
      pthread_create(&thread_4, NULL, getDiagramHelperThreaded, (void *)args4);

      pthread_join(thread_1, NULL);
      pthread_join(thread_2, NULL);
      pthread_join(thread_3, NULL);
      pthread_join(thread_4, NULL);

    } else {
      getDiagramHelperThreaded((void *)args1);
      getDiagramHelperThreaded((void *)args2);
      getDiagramHelperThreaded((void *)args3);
      getDiagramHelperThreaded((void *)args4);
    }

    // free
    for (int i = 0; i < 4; i++) {
      free(firstQuadrantCorners[i]);
      free(secondQuadrantCorners[i]);
      free(thirdQuadrantCorners[i]);
      free(fourthQuadrantCorners[i]);
    }

    free(firstQuadrantCorners);
    free(secondQuadrantCorners);
    free(thirdQuadrantCorners);
    free(fourthQuadrantCorners);

    free(args1);
    free(args2);
    free(args3);
    free(args4);
  }
  return NULL;
};

struct Seed **getSeeds(int matrixSize, int numberSeeds) {
  // complete according to above python reference
  struct Seed **seeds =
      (struct Seed **)malloc(numberSeeds * sizeof(struct Seed *));
  for (int i = 0; i < numberSeeds; i++) {
    seeds[i] = (struct Seed *)malloc(sizeof(struct Seed));
  }

  for (int i = 0; i < numberSeeds; i++) {
    while (1) {
      seeds[i]->x = rand() % matrixSize;
      seeds[i]->y = rand() % matrixSize;

      // check wether x and y are not already in seeds
      int isIn = 0;
      for (int j = 0; j < i; j++) {
        if (seeds[j]->x == seeds[i]->x && seeds[j]->y == seeds[i]->y) {
          isIn = 1;
          break;
        }
      }
      if (!isIn) {
        break;
      }
    }
  }

  return seeds;
};

void printfVoronoiMatrix(struct VoronoiDiagram *voronoiDiagram) {
  char str[] = "$@B\%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'.";
  for (int i = 0; i < voronoiDiagram->n; i++) {
    for (int j = 0; j < voronoiDiagram->n; j++) {
      printf("%c%c", (char)str[voronoiDiagram->matrix[i][j]%sizeof(str)]-1, (char)str[voronoiDiagram->matrix[i][j]%sizeof(str)]-1);
    }
    printf("\n");
  }
}

int main(int argc, char *argv[]) {
   threadsNumber = atoi(argv[4]);
  /* srand(time(NULL)); */
  // get length int from argv[2]
  int length2 = atoi(argv[2]);
  // get number of seeds int from argv[3]
  int numberofSeeds = atoi(argv[3]);
  /* int length2 = 10; */
  /* int numberofSeeds = 100; */

  int n = pow(2, length2);

  struct Seed **seeds = getSeeds(n, numberofSeeds);

  struct VoronoiDiagram *voronoiDiagram =
      constructorVoronoiDiagram(n, seeds, numberofSeeds);

  int **corners = (int **)malloc(4 * sizeof(int *));
  for (int i = 0; i < 4; i++) {
    corners[i] = (int *)malloc(2 * sizeof(int));
  }

  corners[0][0] = 0;
  corners[0][1] = 0;

  corners[1][0] = n - 1;
  corners[1][1] = 0;

  corners[2][0] = n - 1;
  corners[2][1] = n - 1;

  corners[3][0] = 0;
  corners[3][1] = n - 1;

  struct VoronoiArguments *args =
      (struct VoronoiArguments *)malloc(sizeof(struct VoronoiArguments));

  args->diagram = voronoiDiagram;
  args->corners = corners;
  args->threadCounter = 1;

  /* getDiagramHelperNonThreaded(corners, voronoiDiagram); */

  if (strcmp(argv[1], "1") == 0) {
    /* clock_t begin = clock(); */
    /* getDiagramHelperThreaded((void *)args); */
    /* clock_t end = clock(); */
    /* double time_spent = (double)(end - begin) / CLOCKS_PER_SEC; */
    /* printf("Threaded: %f\n", time_spent); */

    struct timeval start, end;
    gettimeofday(&start, NULL);
    getDiagramHelperThreaded((void *)args);
    gettimeofday(&end, NULL);
    double time_spent = (double)(end.tv_sec - start.tv_sec) +
                        (double)(end.tv_usec - start.tv_usec) / 1000000;
    printf("Threaded: %f\n", time_spent);
    printf("Estimated number of threads: %d\n", (int) pow(4, threadsNumber));
    /* printfVoronoiMatrix(voronoiDiagram); */
  } else {
    /* clock_t begin2 = clock(); */
    /* getDiagramHelperNonThreaded(corners, voronoiDiagram); */
    /* clock_t end2 = clock(); */
    /* double time_spent2 = (double)(end2 - begin2) / CLOCKS_PER_SEC; */
    /* printf("Non threaded: %f\n", time_spent2); */

    struct timeval start, end;
    gettimeofday(&start, NULL);
    getDiagramHelperNonThreaded(corners, voronoiDiagram);
    gettimeofday(&end, NULL);
    double time_spent = (double)(end.tv_sec - start.tv_sec) +
                        (double)(end.tv_usec - start.tv_usec) / 1000000;
    printf("Non threaded: %f\n", time_spent);
    /* printfVoronoiMatrix(voronoiDiagram); */
  }

  for (int i = 0; i < voronoiDiagram->seedsCount; i++) {
    free(voronoiDiagram->seeds[i]);
  }
  free(voronoiDiagram->seeds);

  free(voronoiDiagram);

  for (int i = 0; i < 4; i++) {
    free(corners[i]);
  }
  free(corners);

  for (int i = 0; i < numberofSeeds; i++) {
    free(seeds[i]);
  }

  free(args);

  free(seeds);
  return 0;
};
