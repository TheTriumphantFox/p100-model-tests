//
// This is only a SKELETON file for the 'Two Bucket' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class TwoBucket {
  /**
   * Create a new TwoBucket instance.
   *
   * @param {number} bucketOneSize - capacity of bucket one
   * @param {number} bucketTwoSize - capacity of bucket two
   * @param {number} goal - desired amount of water
   * @param {string} startBucket - which bucket to fill first ("one" or "two")
   */
  constructor(bucketOneSize, bucketTwoSize, goal, startBucket) {
    // Validate input types
    if (
      typeof bucketOneSize !== 'number' ||
      typeof bucketTwoSize !== 'number' ||
      typeof goal !== 'number' ||
      typeof startBucket !== 'string'
    ) {
      throw new Error('Invalid input types');
    }

    // Store properties for later use
    this.bucketOneSize = bucketOneSize;
    this.bucketTwoSize = bucketTwoSize;
    this.goal = goal;
    this.startBucket = startBucket;

    // If goal is larger than both buckets, impossible
    if (goal > Math.max(bucketOneSize, bucketTwoSize)) {
      throw new Error('Goal is larger than both bucket capacities');
    }

    // If goal is not reachable (gcd check)
    const gcd = (a, b) => (b === 0 ? a : gcd(b, a % b));
    if (goal % gcd(bucketOneSize, bucketTwoSize) !== 0) {
      throw new Error('Goal is not reachable with these bucket sizes');
    }
  }

  /**
   * Solve the two bucket problem.
   *
   * @returns {{moves: number, goalBucket: string, otherBucket: number}}
   */
  solve() {
    const { bucketOneSize, bucketTwoSize, goal, startBucket } = this;

    // Helper to perform the simulation
    const simulate = (fromSize, toSize, fromName, toName) => {
      let from = 0;
      let to = 0;
      let moves = 0;

      // First action: fill the starting bucket
      from = fromSize;
      moves++;

      while (true) {
        // Check if goal reached
        if (from === goal) {
          return { moves, goalBucket: fromName, otherBucket: to };
        }
        if (to === goal) {
          return { moves, goalBucket: toName, otherBucket: from };
        }

        // Pour from 'from' to 'to'
        const transfer = Math.min(from, toSize - to);
        from -= transfer;
        to += transfer;
        moves++;

        // After pouring, check goal again
        if (from === goal) {
          return { moves, goalBucket: fromName, otherBucket: to };
        }
        if (to === goal) {
          return { moves, goalBucket: toName, otherBucket: from };
        }

        // If 'from' is empty, fill it
        if (from === 0) {
          from = fromSize;
          moves++;
        }

        // If 'to' is full, empty it
        if (to === toSize) {
          to = 0;
          moves++;
        }
      }
    };

    // Determine which simulation to run based on startBucket
    if (startBucket === 'one') {
      return simulate(bucketOneSize, bucketTwoSize, 'one', 'two');
    } else if (startBucket === 'two') {
      return simulate(bucketTwoSize, bucketOneSize, 'two', 'one');
    } else {
      throw new Error('startBucket must be "one" or "two"');
    }
  }
}
