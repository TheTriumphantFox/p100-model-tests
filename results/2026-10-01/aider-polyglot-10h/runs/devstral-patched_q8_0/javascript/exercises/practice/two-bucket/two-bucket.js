export class TwoBucket {
  constructor(bucketOneSize, bucketTwoSize, desiredAmount, startBucket) {
    // Validate inputs
    if (desiredAmount > bucketOneSize && desiredAmount > bucketTwoSize) {
      throw new Error('Goal larger than both buckets');
    }

    if (desiredAmount % Math.gcd(bucketOneSize, bucketTwoSize) !== 0) {
      throw new Error('Goal not reachable with given bucket sizes');
    }

    this.bucketOneSize = bucketOneSize;
    this.bucketTwoSize = bucketTwoSize;
    this.desiredAmount = desiredAmount;
    this.startBucket = startBucket;
    this.bucketOne = 0;
    this.bucketTwo = 0;
  }

  solve() {
    // Fill the starting bucket
    if (this.startBucket === 'one') {
      this.bucketOne = this.bucketOneSize;
    } else {
      this.bucketTwo = this.bucketTwoSize;
    }

    // BFS to find the solution
    const queue = [{ one: this.bucketOne, two: this.bucketTwo, moves: 1 }];
    const visited = new Set();
    visited.add(`${this.bucketOne},${this.bucketTwo}`);

    while (queue.length > 0) {
      const current = queue.shift();
      const { one, two, moves } = current;

      // Check if we've reached the desired amount
      if (one === this.desiredAmount || two === this.desiredAmount) {
        return {
          moves: moves,
          goalBucket: one === this.desiredAmount ? 'one' : 'two',
          otherBucket: one === this.desiredAmount ? two : one
        };
      }

      // Generate all possible next states
      const nextStates = this.generateNextStates(one, two);

      for (const state of nextStates) {
        const key = `${state.one},${state.two}`;
        if (!visited.has(key)) {
          visited.add(key);
          queue.push({ ...state, moves: moves + 1 });
        }
      }
    }

    // If no solution found (shouldn't happen due to constructor validation)
    return {
      moves: -1,
      goalBucket: null,
      otherBucket: null
    };
  }

  generateNextStates(one, two) {
    const states = [];

    // Fill bucket one
    if (one < this.bucketOneSize) {
      const newOne = this.bucketOneSize;
      const newTwo = two;
      states.push({ one: newOne, two: newTwo });
    }

    // Fill bucket two
    if (two < this.bucketTwoSize) {
      const newOne = one;
      const newTwo = this.bucketTwoSize;
      states.push({ one: newOne, two: newTwo });
    }

    // Empty bucket one
    if (one > 0) {
      const newOne = 0;
      const newTwo = two;
      // Check if this violates the rule
      if (!(newOne === 0 && newTwo === this.bucketTwoSize && this.startBucket === 'one')) {
        states.push({ one: newOne, two: newTwo });
      }
    }

    // Empty bucket two
    if (two > 0) {
      const newOne = one;
      const newTwo = 0;
      // Check if this violates the rule
      if (!(newOne === 0 && newTwo === 0 && this.startBucket === 'two')) {
        states.push({ one: newOne, two: newTwo });
      }
    }

    // Pour from bucket one to bucket two
    if (one > 0 && two < this.bucketTwoSize) {
      const pourAmount = Math.min(one, this.bucketTwoSize - two);
      const newOne = one - pourAmount;
      const newTwo = two + pourAmount;
      states.push({ one: newOne, two: newTwo });
    }

    // Pour from bucket two to bucket one
    if (two > 0 && one < this.bucketOneSize) {
      const pourAmount = Math.min(two, this.bucketOneSize - one);
      const newOne = one + pourAmount;
      const newTwo = two - pourAmount;
      states.push({ one: newOne, two: newTwo });
    }

    return states;
  }
}

// Helper function to calculate GCD
function gcd(a, b) {
  while (b !== 0) {
    const temp = b;
    b = a % b;
    a = temp;
  }
  return a;
}
