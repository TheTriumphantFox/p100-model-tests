WHITE = "W"
BLACK = "B"
EMPTY = ""

class Board:
    """Count territories of each player in a Go game

    Args:
        board (list[str]): A two-dimensional Go board
    """

    def __init__(self, board):
        self.board = board
        self.height = len(board)
        self.width = len(board[0]) if self.height > 0 else 0

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
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError('Invalid coordinate')

        if self.board[y][x] != ' ':
            return (EMPTY, set())

        # BFS to find connected empty spaces
        visited = set()
        queue = [(x, y)]
        territories = set()
        owners = set()

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            
            stone = self.board[cy][cx]
            if stone == ' ':
                territories.add((cx, cy))
                # Check neighbors
                neighbors = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]
                for nx, ny in neighbors:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in visited:
                            if self.board[ny][nx] == ' ':
                                queue.append((nx, ny))
                            else:
                                owners.add(self.board[ny][nx])
            else:
                # This shouldn't happen for the starting point if we checked it, 
                # but if we encounter a stone during traversal (shouldn't happen with this logic)
                pass

        if len(owners) == 1:
            owner = owners.pop()
        else:
            owner = EMPTY
            
        return (owner, territories)

    def territories(self):
        """Find the owners and the territories of the whole board

        Args:
            none

        Returns:
            dict(str, set): A dictionary whose key being the owner
                        , i.e. "W", "B", "".  The value being a set
                        of coordinates owned by the owner.
        """
        result = {WHITE: set(), BLACK: set(), EMPTY: set()}
        visited = set()
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in visited:
                    continue
                if self.board[y][x] != ' ':
                    continue
                
                # BFS for this territory group
                queue = [(x, y)]
                group_visited = set()
                territories = set()
                owners = set()
                
                while queue:
                    cx, cy = queue.pop(0)
                    if (cx, cy) in group_visited:
                        continue
                    group_visited.add((cx, cy))
                    visited.add((cx, cy))
                    
                    stone = self.board[cy][cx]
                    if stone == ' ':
                        territories.add((cx, cy))
                        neighbors = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]
                        for nx, ny in neighbors:
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if (nx, ny) not in group_visited:
                                    if self.board[ny][nx] == ' ':
                                        queue.append((nx, ny))
                                    else:
                                        owners.add(self.board[ny][nx])
                
                if len(owners) == 1:
                    owner = owners.pop()
                    result[owner].update(territories)
                else:
                    result[EMPTY].update(territories)
                    
        return result
