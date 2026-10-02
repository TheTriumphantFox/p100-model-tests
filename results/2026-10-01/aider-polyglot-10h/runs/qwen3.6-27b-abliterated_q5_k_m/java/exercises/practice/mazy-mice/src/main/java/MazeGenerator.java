import java.util.Random;
import java.util.Stack;
import java.util.ArrayList;
import java.util.List;

public class MazeGenerator {

    public char[][] generatePerfectMaze(int rows, int columns) {
        return generatePerfectMaze(rows, columns, new Random().nextInt());
    }

    public char[][] generatePerfectMaze(int rows, int columns, int seed) {
        if (rows < 5 || rows > 100 || columns < 5 || columns > 100) {
            throw new IllegalArgumentException();
        }

        Random random = new Random(seed);

        // The maze grid dimensions for characters
        int height = 2 * rows + 1;
        int width = 2 * columns + 1;
        char[][] grid = new char[height][width];

        // Visited array for maze generation (cells are at odd indices)
        boolean[][] visited = new boolean[rows][columns];
        
        // Start at a random cell
        int startR = random.nextInt(rows);
        int startC = random.nextInt(columns);
        
        // Stack for DFS
        Stack<int[]> stack = new Stack<>();
        stack.push(new int[]{startR, startC});
        visited[startR][startC] = true;

        // Directions: Top, Right, Bottom, Left
        int[] dr = {-1, 0, 1, 0};
        int[] dc = {0, 1, 0, -1};

        // Horizontal walls: hWalls[r][c] is the wall between cell (r,c) and (r,c+1)
        boolean[][] hWalls = new boolean[rows][columns - 1];
        // Vertical walls: vWalls[r][c] is the wall between cell (r,c) and (r+1,c)
        boolean[][] vWalls = new boolean[rows - 1][columns];

        // Initialize all walls as present
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < columns - 1; c++) {
                hWalls[r][c] = true;
            }
        }
        for (int r = 0; r < rows - 1; r++) {
            for (int c = 0; c < columns; c++) {
                vWalls[r][c] = true;
            }
        }

        while (!stack.isEmpty()) {
            int[] current = stack.peek();
            int r = current[0];
            int c = current[1];

            List<Integer> neighbors = new ArrayList<>();
            for (int i = 0; i < 4; i++) {
                int nr = r + dr[i];
                int nc = c + dc[i];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < columns && !visited[nr][nc]) {
                    neighbors.add(i);
                }
            }

            if (!neighbors.isEmpty()) {
                int dir = neighbors.get(random.nextInt(neighbors.size()));
                int nr = r + dr[dir];
                int nc = c + dc[dir];
                
                // Remove wall
                if (dir == 0) { // Top
                    vWalls[nr][nc] = false;
                } else if (dir == 1) { // Right
                    hWalls[r][nc] = false;
                } else if (dir == 2) { // Bottom
                    vWalls[r][c] = false;
                } else if (dir == 3) { // Left
                    hWalls[r][nc] = false;
                }

                visited[nr][nc] = true;
                stack.push(new int[]{nr, nc});
            } else {
                stack.pop();
            }
        }

        // Fill grid with spaces for rooms
        for (int r = 0; r < height; r++) {
            for (int c = 0; c < width; c++) {
                if (r % 2 == 1 && c % 2 == 1) {
                    grid[r][c] = ' ';
                } else {
                    grid[r][c] = ' '; // Placeholder
                }
            }
        }

        // Determine entrance and exit rows (random odd indices)
        int entranceRow = 1 + 2 * random.nextInt(rows);
        int exitRow = 1 + 2 * random.nextInt(rows);

        // Render walls and junctions
        for (int r = 0; r < height; r++) {
            for (int c = 0; c < width; c++) {
                if (r % 2 == 1 && c % 2 == 1) {
                    continue; // Room
                }

                boolean top = false, bottom = false, left = false, right = false;

                // Check neighbors for passages
                if (r > 0 && grid[r-1][c] == ' ') top = true;
                if (r < height - 1 && grid[r+1][c] == ' ') bottom = true;
                if (c > 0 && grid[r][c-1] == ' ') left = true;
                if (c < width - 1 && grid[r][c+1] == ' ') right = true;

                // Also check wall removals for internal walls
                if (r % 2 == 0 && c % 2 == 1) {
                    // Horizontal wall segment
                    int cellR = r / 2;
                    int cellC = (c - 1) / 2;
                    // Wall is between (cellR, cellC) and (cellR, cellC+1)
                    if (cellC >= 0 && cellC < columns - 1) {
                        if (!hWalls[cellR][cellC]) {
                            // Passage exists, so left and right should be true if rooms exist
                            // But we already checked grid neighbors.
                            // If the wall is removed, the rooms are connected.
                            // The grid cells above/below are rooms.
                            // So if wall is removed, this position is a passage.
                            // But our grid check for left/right already handles this if rooms are marked ' '.
                            // Wait, if hWalls is false, then (r, c-1) and (r, c+1) are rooms, so left/right are true.
                        }
                    }
                } else if (r % 2 == 1 && c % 2 == 0) {
                    // Vertical wall segment
                    int cellR = (r - 1) / 2;
                    int cellC = c / 2;
                    // Wall is between (cellR, cellC) and (cellR+1, cellC)
                    if (cellR >= 0 && cellR < rows - 1) {
                        if (!vWalls[cellR][cellC]) {
                            // Passage exists
                        }
                    }
                }

                // Assign character based on connections
                if (top && bottom && left && right) grid[r][c] = '┼';
                else if (top && bottom && left) grid[r][c] = '┤';
                else if (top && bottom && right) grid[r][c] = '├';
                else if (top && left && right) grid[r][c] = '┬';
                else if (bottom && left && right) grid[r][c] = '┴';
                else if (top && bottom) grid[r][c] = '│';
                else if (left && right) grid[r][c] = '─';
                else if (top && left) grid[r][c] = '┐';
                else if (top && right) grid[r][c] = '┌';
                else if (bottom && left) grid[r][c] = '┘';
                else if (bottom && right) grid[r][c] = '└';
                else if (top) grid[r][c] = '│';
                else if (bottom) grid[r][c] = '│';
                else if (left) grid[r][c] = '─';
                else if (right) grid[r][c] = '─';
                else grid[r][c] = ' '; // Should be rare, maybe corners
            }
        }

        // Handle borders and corners
        // Top border
        for (int c = 0; c < width; c++) {
            if (c % 2 == 0) grid[0][c] = '┌'; // Corner or T
            else grid[0][c] = '─';
        }
        // Bottom border
        for (int c = 0; c < width; c++) {
            if (c % 2 == 0) grid[height-1][c] = '└';
            else grid[height-1][c] = '─';
        }
        // Left border
        for (int r = 0; r < height; r++) {
            if (r % 2 == 0) grid[r][0] = '┌';
            else grid[r][0] = '│';
        }
        // Right border
        for (int r = 0; r < height; r++) {
            if (r % 2 == 0) grid[r][width-1] = '┐';
            else grid[r][width-1] = '│';
        }

        // Refine corners
        grid[0][0] = '┌';
        grid[0][width-1] = '┐';
        grid[height-1][0] = '└';
        grid[height-1][width-1] = '┘';

        // Add entrance and exit
        grid[entranceRow][0] = '⇨';
        grid[exitRow][width-1] = '⇨';

        return grid;
    }
}
