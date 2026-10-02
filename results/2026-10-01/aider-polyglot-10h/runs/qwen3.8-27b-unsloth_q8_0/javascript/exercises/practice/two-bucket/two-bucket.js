//
// This is only a SKELETON file for the 'Two Bucket' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class TwoBucket {
  constructor(
    startBucket,
    goal,
    sizeOfBucketOne,
    sizeOfBucketTwo,
  ) {
    this.startBucket = startBucket;
    this.goal = goal;
    this.sizeOfBucketOne = sizeOfBucketOne;
    this.sizeOfBucketTwo = sizeOfBucketTwo;
  }

  solve() {
    const { startBucket, goal, sizeOfBucketOne, sizeOfBucketTwo } = this;

    if (goal > sizeOfBucketOne && goal > sizeOfBucketTwo) {
      throw new Error('No solution possible since input is greater than both buckets');
    }

    if (goal % this.gcd(sizeOfBucketOne, sizeOfBucketTwo) !== 0) {
      throw new Error('No solution possible since goal is not a multiple of the GCD of the bucket sizes');
    }

    const startState =
      startBucket === 'one'
        ? [0, 0]
        : [0, 0]; // Initial state is always empty before first move

    // We start by filling the start bucket as the first move
    let initialState;
    if (startBucket === 'one') {
      initialState = [sizeOfBucketOne, 0];
    } else {
      initialState = [0, sizeOfBucketTwo];
    }

    // Check if initial state is already the goal
    if (initialState[0] === goal || initialState[1] === goal) {
      return this.formatResult(1, initialState);
    }

    const visited = new Set();
    visited.add(this.stateKey(initialState));

    const queue = [{ state: initialState, moves: 1 }];

    while (queue.length > 0) {
      const { state, moves } = queue.shift();
      const [b1, b2] = state;

      const nextStates = this.getNextStates(b1, b2, startBucket);

      for (const nextState of nextStates) {
        const key = this.stateKey(nextState);
        if (visited.has(key)) continue;
        
        // Rule: After an action, you may not arrive at a state where the 
        // initial starting bucket is empty and the other bucket is full.
        if (startBucket === 'one') {
          if (nextState[0] === 0 && nextState[1] === sizeOfBucketTwo) {
            continue;
          }
        } else {
          if (nextState[1] === 0 && nextState[0] === sizeOfBucketOne) {
            continue;
          }
        }

        visited.add(key);
        const newMoves = moves + 1;

        if (nextState[0] === goal || nextState[1] === goal) {
          return this.formatResult(newMoves, nextState);
        }

        queue.push({ state: nextState, moves: newMoves });
      }
    }

    throw new Error('No solution possible');
  }

  getNextStates(b1, b2, startBucket) {
    const { sizeOfBucketOne, sizeOfBucketTwo } = this;
    const states = [];

    // 1. Fill bucket 1
    if (b1 !== sizeOfBucketOne) {
      states.push([sizeOfBucketOne, b2]);
    }

    // 2. Fill bucket 2
    if (b2 !== sizeOfBucketTwo) {
      states.push([b1, sizeOfBucketTwo]);
    }

    // 3. Empty bucket 1
    if (b1 !== 0) {
      states.push([0, b2]);
    }

    // 4. Empty bucket 2
    if (b2 !== 0) {
      states.push([b1, 0]);
    }

    // 5. Pour bucket 1 into bucket 2
    if (b1 !== 0 && b2 !== sizeOfBucketTwo) {
      const pourAmount = Math.min(b1, sizeOfBucketTwo - b2);
      states.push([b1 - pourAmount, b2 + pourAmount]);
    }

    // 6. Pour bucket 2 into bucket 1
    if (b2 !== 0 && b1 !== sizeOfBucketOne) {
      const pourAmount = Math.min(b2, sizeOfBucketOne - b1);
      states.push([b1 + pourAmount, b2 - pourAmount]);
    }

    return states;
  }

  stateKey(state) {
    return `${state[0]}-${state[1]}`;
  }

  formatResult(moves, state) {
    const [b1, b2] = state;
    if (b1 === this.goal) {
      return {
        moves,
        goalBucket: 'one',
        otherBucket: b2,
      };
    }
    return {
      moves,
      goalBucket: 'two',
      otherBucket: b1,
    };
  }

  gcd(a, b) {
    while (b !== 0) {
      const temp = b;
      b = a % b;
      a = temp;
    }
    return a;
  }
}
