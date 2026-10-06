//
// This is only a SKELETON file for the 'Two Bucket' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class TwoBucket {
  constructor(sizeOne, sizeTwo, goal, startBucket) {
    this.sizeOne = sizeOne;
    this.sizeTwo = sizeTwo;
    this.goal = goal;
    this.startBucket = startBucket;
  }

  solve() {
    const sizeOne = this.sizeOne;
    const sizeTwo = this.sizeTwo;
    const goal = this.goal;
    const startBucket = this.startBucket;

    // Check for impossibility
    if (goal > Math.max(sizeOne, sizeTwo)) {
      throw new Error('Goal is larger than both buckets');
    }

    const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
    if (goal % gcd(sizeOne, sizeTwo) !== 0) {
      throw new Error('Goal is not reachable');
    }

    // BFS queue: [b1, b2, moves]
    const queue = [];
    const visited = new Set();

    // Helper to add state to queue if not visited and valid
    const addState = (b1, b2, moves) => {
      const key = `${b1},${b2}`;
      if (!visited.has(key)) {
        // Check the rule: "After an action, you may not arrive at a state where the initial starting bucket is empty and the other bucket is full."
        // If start is 'one', forbidden state is (0, sizeTwo)
        // If start is 'two', forbidden state is (sizeOne, 0)
        if (startBucket === 'one' && b1 === 0 && b2 === sizeTwo) {
          return; // Invalid state, do not add
        }
        if (startBucket === 'two' && b1 === sizeOne && b2 === 0) {
          return; // Invalid state, do not add
        }

        visited.add(key);
        queue.push([b1, b2, moves]);
      }
    };

    // Helper to check if goal is reached
    const checkGoal = (b1, b2, moves) => {
      if (b1 === goal) {
        return { moves, goalBucket: 'one', otherBucket: b2 };
      }
      if (b2 === goal) {
        return { moves, goalBucket: 'two', otherBucket: b1 };
      }
      return null;
    };

    // Initial state: both empty
    // First action: Fill the starting bucket
    if (startBucket === 'one') {
      addState(sizeOne, 0, 1);
    } else {
      addState(0, sizeTwo, 1);
    }

    while (queue.length > 0) {
      const [b1, b2, moves] = queue.shift();

      // Check if goal reached
      const result = checkGoal(b1, b2, moves);
      if (result) {
        return result;
      }

      // Generate next states
      // 1. Fill bucket one
      addState(sizeOne, b2, moves + 1);
      // 2. Fill bucket two
      addState(b1, sizeTwo, moves + 1);
      // 3. Empty bucket one
      addState(0, b2, moves + 1);
      // 4. Empty bucket two
      addState(b1, 0, moves + 1);
      // 5. Pour bucket one into bucket two
      const pour1to2 = Math.min(b1, sizeTwo - b2);
      addState(b1 - pour1to2, b2 + pour1to2, moves + 1);
      // 6. Pour bucket two into bucket one
      const pour2to1 = Math.min(b2, sizeOne - b1);
      addState(b1 + pour2to1, b2 - pour2to1, moves + 1);
    }

    throw new Error('No solution found');
  }
}
