#include <math.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

struct Seed {
  int id;
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

  return voronoiDiagram;
}

double distance(struct Seed *seed, int x, int y) {
  return sqrt(pow(seed->x - x, 2) + pow(seed->y - y, 2));
}

void getDiagramHelperNonThreaded(int **corners,
                                 struct VoronoiDiagram *voronoiDiagram) {
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
        voronoiDiagram->matrix[height][width] = closestSeeds[0]->id;
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

/*
  def getRandomSeeds(n: int, k: int) -> list[Seed]:
    seeds = []
    for i in range(k):
        while True:
            x = randint(0, n - 1)
            y = randint(0, n - 1)
            seed = Seed(i, x, y)
            if seed not in seeds:
                seeds.append(seed)
                break
    return seeds

  */

struct Seed **getSeeds(int matrixSize, int numberSeeds) {
  // complete according to above python reference
  struct Seed **seeds =
      (struct Seed **)malloc(numberSeeds * sizeof(struct Seed *));
  for (int i = 0; i < numberSeeds; i++) {
    seeds[i] = (struct Seed *)malloc(sizeof(struct Seed));
  }

  for (int i = 0; i < numberSeeds; i++) {
    while (1) {
      seeds[i]->id = i;
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

int main(int argc, char *argv[]) {
  srand(time(NULL));
  int n = 1024;
  int numberofSeeds = 12;

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

  getDiagramHelperNonThreaded(corners, voronoiDiagram);

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      // printf formatted
      printf("%d ", voronoiDiagram->matrix[i][j]);
    }
    printf("\n");
  }

  /* // free */

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

  free(seeds);
  return 0;
};
