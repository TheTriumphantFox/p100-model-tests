from collections import deque

WHITE = "W"
BLACK = "B"


class Board:
    """Count territories of each player in a Go game

    Args:
        board (list[str]): A two-dimensional Go board
    """

    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0]) if self.rows > 0 else 0

    def territory(self, x, y):
        """Find the owner and the territories given a coordinate on
           the board

        Args:
            x (int): Column on the board
            y (int): Row on the board

        Returns:
            (str, set): A tuple, the first element being the owner
                        of that area.  One of "W", "B", "".  The
                        second being a set of coordinates, representing
                        the owner's territories.
        """
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            raise ValueError('Invalid coordinate')

        if self.board[y][x] != ' ':
            return "", set()

        # Flood fill to find all connected empty spaces
        visited = set()
        queue = deque([(x, y)])
        territory_coords = set()
        owners = set()

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            
            visited.add((cx, cy))
            territory_coords.add((cx, cy))

            # Check neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if self.board[ny][nx] == ' ':
                        if (nx, ny) not in visited:
                            queue.append((nx, ny))
                    elif self.board[ny][nx] in (WHITE, BLACK):
                        owners.add(self.board[ny][nx])

        # Determine owner
        if len(owners) == 1:
            owner = owners.pop()
        else:
            owner = ""

        return owner, territory_coords

    def territories(self):
        """Find the owners and the territories of the whole board

        Args:
            none

        Returns:
            dict(str, set): A dictionary whose key being the owner
                        , i.e. "W", "B", "".  The value being a set
                        of coordinates owned by the owner.
        """
        result = {WHITE: set(), BLACK: set(), "": set()}
        
        # We need to avoid processing the same territory multiple times.
        # We can keep track of visited empty coordinates.
        visited_empty = set()

        for y in range(self.rows):
            for x in range(self.cols):
                if self.board[y][x] == ' ' and (x, y) not in visited_empty:
                    owner, territory_coords = self.territory(x, y)
                    visited_empty.update(territory_coords)
                    result[owner].update(territory_coords)

        return result
