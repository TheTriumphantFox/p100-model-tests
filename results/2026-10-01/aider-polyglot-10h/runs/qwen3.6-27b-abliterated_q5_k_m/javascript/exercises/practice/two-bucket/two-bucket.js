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
  }

  solve() {
    // Check if goal is larger than both buckets
    if (this.goal > this.bucketOne && this.goal > this.bucketTwo) {
      throw new Error('Goal larger than both buckets');
    }

    // Check if goal is reachable using GCD
    const gcd = (a, b) => (b === 0 ? a : gcd(b, a % b));
    if (this.goal % gcd(this.bucketOne, this.bucketTwo) !== 0) {
      throw new Error('Goal not reachable');
    }

    const queue = [];
    const visited = new Set();

    let startState;
    if (this.startBucket === 'one') {
      startState = [this.bucketOne, 0];
    } else {
      startState = [0, this.bucketTwo];
    }

    queue.push({ state: startState, moves: 1 });
    visited.add(`${startState[0]},${startState[1]}`);

    while (queue.length > 0) {
      const { state, moves } = queue.shift();
      const [b1, b2] = state;

      if (b1 === this.goal) {
        return {
          moves,
          goalBucket: 'one',
          otherBucket: b2
        };
      }
      if (b2 === this.goal) {
        return {
          moves,
          goalBucket: 'two',
          otherBucket: b1
        };
      }

      const nextStates = [];

      // Pour 1 -> 2
      const pour1to2 = Math.min(b1, this.bucketTwo - b2);
      nextStates.push([b1 - pour1to2, b2 + pour1to2]);

      // Pour 2 -> 1
      const pour2to1 = Math.min(b2, this.bucketOne - b1);
      nextStates.push([b1 + pour2to1, b2 - pour2to1]);

      // Empty 1
      nextStates.push([0, b2]);

      // Empty 2
      nextStates.push([b1, 0]);

      // Fill 1
      nextStates.push([this.bucketOne, b2]);

      // Fill 2
      nextStates.push([b1, this.bucketTwo]);

      for (const nextState of nextStates) {
        const key = `${nextState[0]},${nextState[1]}`;
        if (visited.has(key)) continue;

        // Rule: After an action, you may not arrive at a state where the
        // initial starting bucket is empty and the other bucket is full.
        if (this.startBucket === 'one') {
          if (nextState[0] === 0 && nextState[1] === this.bucketTwo) continue;
        } else {
          if (nextState[0] === this.bucketOne && nextState[1] === 0) continue;
        }

        visited.add(key);
        queue.push({ state: nextState, moves: moves + 1 });
      }
    }

    throw new Error('No solution found');
  }
}
