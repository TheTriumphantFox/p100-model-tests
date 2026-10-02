import java.util.Random;
import java.util.Stack;

public class MazeGenerator {

    public char[][] generatePerfectMaze(int rows, int columns) {
        return generatePerfectMaze(rows, columns, new Random().nextInt());
    }

    public char[][] generatePerfectMaze(int rows, int columns, int seed) {
        if (rows < 5 || rows > 100 || columns < 5 || columns > 100) {
            throw new IllegalArgumentException("Rows and columns must be between 5 and 100");
        }

        Random random = new Random(seed);
        
        // The maze grid will be (2*rows + 1) high and (2*columns + 1) wide
        int height = 2 * rows + 1;
        int width = 2 * columns + 1;

        // Initialize the grid with walls
        char[][] maze = new char[height][width];
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                maze[i][j] = ' '; // Placeholder, will be overwritten
            }
        }

        // We use a boolean grid to track which cells are visited
        // and which walls are removed.
        // Cell (r, c) in the logical maze corresponds to position (2*r + 1, 2*c + 1) in the char grid.
        // Walls between cells are at even coordinates.
        
        boolean[][] visited = new boolean[rows][columns];
        
        // Directions: Up, Down, Left, Right
        int[] dr = {-1, 1, 0, 0};
        int[] dc = {0, 0, -1, 1};

        // Start from a random cell
        int startR = random.nextInt(rows);
        int startC = random.nextInt(columns);
        
        Stack<int[]> stack = new Stack<>();
        stack.push(new int[]{startR, startC});
        visited[startR][startC] = true;

        while (!stack.isEmpty()) {
            int[] current = stack.peek();
            int cr = current[0];
            int cc = current[1];

            // Find unvisited neighbors
            int[] validDirections = new int[4];
            int count = 0;
            for (int i = 0; i < 4; i++) {
                int nr = cr + dr[i];
                int nc = cc + dc[i];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < columns && !visited[nr][nc]) {
                    validDirections[count++] = i;
                }
            }

            if (count == 0) {
                // No unvisited neighbors, backtrack
                stack.pop();
            } else {
                // Pick a random valid direction
                int dirIndex = validDirections[random.nextInt(count)];
                int nr = cr + dr[dirIndex];
                int nc = cc + dc[dirIndex];
                
                visited[nr][nc] = true;
                stack.push(new int[]{nr, nc});
                
                // Remove the wall between current and next
                // The wall is located at the midpoint between (2*cr+1, 2*cc+1) and (2*nr+1, 2*nc+1)
                int wallR = 2 * cr + 1 + dr[dirIndex];
                int wallC = 2 * cc + 1 + dc[dirIndex];
                // We don't store the wall removal in the char grid yet, 
                // we will construct the final grid based on the visited cells and connections.
                // Actually, it's easier to build the grid by checking connections.
            }
        }

        // Now we need to construct the char grid.
        // A cell (r, c) is open.
        // A wall between (r, c) and (r, c+1) is removed if both are visited and connected.
        // In Recursive Backtracking, if we moved from (r,c) to (r,c+1), the wall is removed.
        // We can re-derive the connections or store them. 
        // Let's store the connections in a boolean grid for walls.
        
        // Let's restart the generation logic to properly track walls for rendering.
        // It's cleaner to generate the maze structure first, then render.
        
        return renderMaze(rows, columns, seed);
    }
    
    private char[][] renderMaze(int rows, int columns, int seed) {
        Random random = new Random(seed);
        int height = 2 * rows + 1;
        int width = 2 * columns + 1;

        // wall[r][c] is true if there is a wall at this position in the grid
        // Grid positions:
        // (0,0) is top-left corner
        // (2*r+1, 2*c+1) is cell (r,c)
        // (2*r+1, 2*c+2) is wall between (r,c) and (r,c+1)
        // (2*r+2, 2*c+1) is wall between (r,c) and (r+1,c)
        
        boolean[][] wall = new boolean[height][width];
        
        // Initialize all as walls
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                wall[i][j] = true;
            }
        }

        // Mark cells as not walls
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < columns; c++) {
                wall[2 * r + 1][2 * c + 1] = false;
            }
        }

        boolean[][] visited = new boolean[rows][columns];
        int[] dr = {-1, 1, 0, 0};
        int[] dc = {0, 0, -1, 1};

        int startR = random.nextInt(rows);
        int startC = random.nextInt(columns);
        
        Stack<int[]> stack = new Stack<>();
        stack.push(new int[]{startR, startC});
        visited[startR][startC] = true;

        while (!stack.isEmpty()) {
            int[] current = stack.peek();
            int cr = current[0];
            int cc = current[1];

            int[] validDirections = new int[4];
            int count = 0;
            for (int i = 0; i < 4; i++) {
                int nr = cr + dr[i];
                int nc = cc + dc[i];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < columns && !visited[nr][nc]) {
                    validDirections[count++] = i;
                }
            }

            if (count == 0) {
                stack.pop();
            } else {
                int dirIndex = validDirections[random.nextInt(count)];
                int nr = cr + dr[dirIndex];
                int nc = cc + dc[dirIndex];
                
                visited[nr][nc] = true;
                stack.push(new int[]{nr, nc});
                
                // Remove wall between (cr, cc) and (nr, nc)
                int wallR = 2 * cr + 1 + dr[dirIndex];
                int wallC = 2 * cc + 1 + dc[dirIndex];
                wall[wallR][wallC] = false;
            }
        }

        // Convert wall grid to char grid with box drawing
        char[][] maze = new char[height][width];
        
        for (int r = 0; r < height; r++) {
            for (int c = 0; c < width; c++) {
                if (!wall[r][c]) {
                    maze[r][c] = ' ';
                } else {
                    // Determine box drawing character
                    // Check neighbors
                    boolean up = r > 0 && wall[r-1][c];
                    boolean down = r < height - 1 && wall[r+1][c];
                    boolean left = c > 0 && wall[r][c-1];
                    boolean right = c < width - 1 && wall[r][c+1];
                    
                    // Note: For the outer border, the "outside" is not a wall, so we treat it as false for connection purposes?
                    // Actually, the outer border walls are connected to each other.
                    // The logic above checks if the adjacent grid cell is a wall.
                    // For the top border (r=0), up is false.
                    // For the left border (c=0), left is false.
                    
                    if (up && down && left && right) {
                        maze[r][c] = '┼';
                    } else if (up && left && right) {
                        maze[r][c] = '┬';
                    } else if (down && left && right) {
                        maze[r][c] = '┴';
                    } else if (up && down && right) {
                        maze[r][c] = '├';
                    } else if (up && down && left) {
                        maze[r][c] = '┤';
                    } else if (left && right) {
                        maze[r][c] = '─';
                    } else if (up && down) {
                        maze[r][c] = '│';
                    } else if (down && right) {
                        maze[r][c] = '┌';
                    } else if (down && left) {
                        maze[r][c] = '┐';
                    } else if (up && right) {
                        maze[r][c] = '└';
                    } else if (up && left) {
                        maze[r][c] = '┘';
                    } else {
                        // Should not happen for a connected maze, but fallback
                        maze[r][c] = ' ';
                    }
                }
            }
        }

        // Add entrance and exit
        // Entrance on the left, Exit on the right
        // Let's place them in the middle row
        int midRow = rows / 2;
        int entranceGridRow = 2 * midRow + 1;
        int exitGridRow = 2 * midRow + 1;
        
        maze[entranceGridRow][0] = '⇨';
        maze[exitGridRow][width - 1] = '⇨';

        return maze;
    }
}
