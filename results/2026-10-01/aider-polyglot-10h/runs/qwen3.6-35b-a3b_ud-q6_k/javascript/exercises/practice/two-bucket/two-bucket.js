//
// This is only a SKELETON file for the 'Two Bucket' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class TwoBucket {
  constructor(bucketOne, bucketTwo, goal, startBucket) {
    this.bucketOne = bucketOne;
    this.bucketTwo = bucketTwo;
    this.goal = goal;
    this.startBucket = startBucket;

    const gcd = this.gcd(bucketOne, bucketTwo);
    if (goal % gcd !== 0) {
      throw new Error('The goal must be achievable by changing amount of water in buckets to multiples of the greatest common divisor of these buckets.');
    }
    if (goal > bucketOne && goal > bucketTwo) {
      throw new Error('Goal cannot be reached if it is larger than both buckets.');
    }

    const visited = new Set();
    const queue = [];

    let startState;
    let startMoves = 1;

    if (this.startBucket === 'one') {
      startState = [bucketOne, 0];
    } else {
      startState = [0, bucketTwo];
    }

    // Check if start state is already the goal
    if (startState[0] === goal) {
      this.result = {
        moves: startMoves,
        goalBucket: 'one',
        otherBucket: startState[1]
      };
      return;
    }
    if (startState[1] === goal) {
      this.result = {
        moves: startMoves,
        goalBucket: 'two',
        otherBucket: startState[0]
      };
      return;
    }

    queue.push({
      b1: startState[0],
      b2: startState[1],
      moves: startMoves
    });
    visited.add(startState.join(','));

    while (queue.length > 0) {
      const current = queue.shift();
      const { b1, b2, moves } = current;

      const nextStates = [];

      // Pour bucket one into bucket two
      const pour1to2 = Math.min(b1, bucketTwo - b2);
      nextStates.push([b1 - pour1to2, b2 + pour1to2]);

      // Pour bucket two into bucket one
      const pour2to1 = Math.min(b2, bucketOne - b1);
      nextStates.push([b1 + pour2to1, b2 - pour2to1]);

      // Empty bucket one
      nextStates.push([0, b2]);

      // Empty bucket two
      nextStates.push([b1, 0]);

      // Fill bucket one
      nextStates.push([bucketOne, b2]);

      // Fill bucket two
      nextStates.push([b1, bucketTwo]);

      for (const [nb1, nb2] of nextStates) {
        const stateKey = `${nb1},${nb2}`;
        
        // Rule: After an action, you may not arrive at a state where the initial starting bucket is empty and the other bucket is full.
        if (this.startBucket === 'one' && nb1 === 0 && nb2 === bucketTwo) {
          continue;
        }
        if (this.startBucket === 'two' && nb1 === bucketOne && nb2 === 0) {
          continue;
        }

        if (!visited.has(stateKey)) {
          visited.add(stateKey);
          
          if (nb1 === goal) {
            this.result = {
              moves: moves + 1,
              goalBucket: 'one',
              otherBucket: nb2
            };
            return;
          }
          if (nb2 === goal) {
            this.result = {
              moves: moves + 1,
              goalBucket: 'two',
              otherBucket: nb1
            };
            return;
          }

          queue.push({
            b1: nb1,
            b2: nb2,
            moves: moves + 1
          });
        }
      }
    }

    throw new Error('Goal not reachable');
  }

  gcd(a, b) {
    if (!b) {
      return a;
    }
    return this.gcd(b, a % b);
  }

  solve() {
    return this.result;
  }
}
