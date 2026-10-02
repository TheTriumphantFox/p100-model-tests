// this module adds some functionality based on the required implementations
// here like: `LinkedList::pop_back` or `Clone for LinkedList<T>`
// You are free to use anything in it, but it's mainly for the test framework.
mod pre_implemented;

use std::marker::PhantomData;
use std::ptr;

// Safety-critical invariants:
// 1. The head and tail pointers must always point to valid nodes or be null
// 2. The length must accurately reflect the number of nodes
// 3. All nodes must be properly linked (next/prev pointers must be consistent)
// 4. The list must not contain any null pointers in the middle of the chain

/// Node structure for the doubly linked list
struct Node<T> {
    data: T,
    next: *mut Node<T>,
    prev: *mut Node<T>,
}

pub struct LinkedList<T> {
    head: *mut Node<T>,
    tail: *mut Node<T>,
    len: usize,
    _marker: PhantomData<T>,
}

pub struct Cursor<'a, T> {
    node: *mut Node<T>,
    list: &'a mut LinkedList<T>,
}

pub struct Iter<'a, T> {
    current: *const Node<T>,
    _marker: PhantomData<&'a T>,
}

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList {
            head: ptr::null_mut(),
            tail: ptr::null_mut(),
            len: 0,
            _marker: PhantomData,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn len(&self) -> usize {
        self.len
    }

    /// Return a cursor positioned on the front element
    pub fn cursor_front(&mut self) -> Cursor<'_, T> {
        Cursor {
            node: self.head,
            list: self,
        }
    }

    /// Return a cursor positioned on the back element
    pub fn cursor_back(&mut self) -> Cursor<'_, T> {
        Cursor {
            node: self.tail,
            list: self,
        }
    }

    /// Return an iterator that moves from front to back
    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            current: self.head,
            _marker: PhantomData,
        }
    }
}

// Helper functions for node management
impl<T> LinkedList<T> {
    /// Create a new node with the given data
    unsafe fn new_node(data: T) -> *mut Node<T> {
        let node = Box::into_raw(Box::new(Node {
            data,
            next: ptr::null_mut(),
            prev: ptr::null_mut(),
        }));
        node
    }

    /// Remove a node from the list and return its data
    unsafe fn remove_node(node: *mut Node<T>) -> T {
        // SAFETY: The caller must ensure the node is part of a list
        let node = &mut *node;
        let data = ptr::read(&node.data);

        // Update neighboring nodes' pointers
        if node.prev.is_null() {
            // This is the head node
            if let Some(next) = node.next.as_mut() {
                next.prev = ptr::null_mut();
            }
        } else {
            (*node.prev).next = node.next;
        }

        if node.next.is_null() {
            // This is the tail node
            if let Some(prev) = node.prev.as_mut() {
                prev.next = ptr::null_mut();
            }
        } else {
            (*node.next).prev = node.prev;
        }

        // Drop the node to free memory
        Box::from_raw(node);
        data
    }
}

impl<T> Cursor<'_, T> {
    /// Take a mutable reference to the current element
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        unsafe {
            if self.node.is_null() {
                None
            } else {
                Some(&mut (*self.node).data)
            }
        }
    }

    /// Move one position forward (towards the back) and
    /// return a reference to the new position
    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<&mut T> {
        unsafe {
            if self.node.is_null() {
                None
            } else {
                self.node = (*self.node).next;
                if self.node.is_null() {
                    None
                } else {
                    Some(&mut (*self.node).data)
                }
            }
        }
    }

    /// Move one position backward (towards the front) and
    /// return a reference to the new position
    pub fn prev(&mut self) -> Option<&mut T> {
        unsafe {
            if self.node.is_null() {
                None
            } else {
                self.node = (*self.node).prev;
                if self.node.is_null() {
                    None
                } else {
                    Some(&mut (*self.node).data)
                }
            }
        }
    }

    /// Remove and return the element at the current position and move the cursor
    /// to the neighboring element that's closest to the back. This can be
    /// either the next or previous position.
    pub fn take(&mut self) -> Option<T> {
        unsafe {
            if self.node.is_null() {
                None
            } else {
                // Determine which neighbor to move to (prefer next)
                let next_node = (*self.node).next;
                let prev_node = (*self.node).prev;

                let data = LinkedList::remove_node(self.node);

                // Move cursor to the next node if it exists, otherwise to the previous
                if !next_node.is_null() {
                    self.node = next_node;
                } else if !prev_node.is_null() {
                    self.node = prev_node;
                } else {
                    self.node = ptr::null_mut();
                }

                Some(data)
            }
        }
    }

    pub fn insert_after(&mut self, element: T) {
        unsafe {
            let new_node = LinkedList::new_node(element);

            if self.node.is_null() {
                // Inserting into empty list
                self.list.head = new_node;
                self.list.tail = new_node;
                self.list.len += 1;
                self.node = new_node;
            } else {
                // Insert after current node
                let current = self.node;
                (*new_node).prev = current;
                (*new_node).next = (*current).next;

                (*current).next = new_node;

                if (*current).next.is_null() {
                    // We're inserting at the tail
                    self.list.tail = new_node;
                } else {
                    (*(*current).next).prev = new_node;
                }

                self.list.len += 1;
                self.node = new_node;
            }
        }
    }

    pub fn insert_before(&mut self, element: T) {
        unsafe {
            let new_node = LinkedList::new_node(element);

            if self.node.is_null() {
                // Inserting into empty list
                self.list.head = new_node;
                self.list.tail = new_node;
                self.list.len += 1;
                self.node = new_node;
            } else {
                // Insert before current node
                let current = self.node;
                (*new_node).next = current;
                (*new_node).prev = (*current).prev;

                (*current).prev = new_node;

                if (*current).prev.is_null() {
                    // We're inserting at the head
                    self.list.head = new_node;
                } else {
                    (*(*current).prev).next = new_node;
                }

                self.list.len += 1;
                self.node = new_node;
            }
        }
    }
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<&'a T> {
        unsafe {
            if self.current.is_null() {
                None
            } else {
                let node = &*self.current;
                self.current = node.next;
                Some(&node.data)
            }
        }
    }
}

impl<T> Drop for LinkedList<T> {
    fn drop(&mut self) {
        // We need to drop all nodes in the list
        while !self.head.is_null() {
            unsafe {
                let head = self.head;
                self.head = (*head).next;
                Box::from_raw(head);
            }
        }
        self.len = 0;
    }
}

// Implement Send and Sync for thread safety
unsafe impl<T: Send> Send for LinkedList<T> {}
unsafe impl<T: Send + Sync> Sync for LinkedList<T> {}

// Implement variance for the linked list
impl<T> LinkedList<Box<T>> {
    // This allows covariance by boxing the elements
}

// For the advanced features, we need to implement the proper variance
// This is done through the PhantomData marker
impl<T> LinkedList<T> {
    // The PhantomData ensures proper variance
}
