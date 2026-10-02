// this module adds some functionality based on the required implementations
// here like: `LinkedList::pop_back` or `Clone for LinkedList<T>`
// You are free to use anything in it, but it's mainly for the test framework.
mod pre_implemented;

use std::marker::PhantomData;
use std::ptr;

struct Node<T> {
    data: T,
    prev: *mut Node<T>,
    next: *mut Node<T>,
}

pub struct LinkedList<T> {
    head: *mut Node<T>,
    tail: *mut Node<T>,
    len: usize,
    marker: PhantomData<T>,
}

pub struct Cursor<'a, T> {
    current: *mut Node<T>,
    list: &'a mut LinkedList<T>,
}

pub struct Iter<'a, T> {
    current: *mut Node<T>,
    marker: PhantomData<&'a T>,
}

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList {
            head: ptr::null_mut(),
            tail: ptr::null_mut(),
            len: 0,
            marker: PhantomData,
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
            current: self.head,
            list: self,
        }
    }

    /// Return a cursor positioned on the back element
    pub fn cursor_back(&mut self) -> Cursor<'_, T> {
        Cursor {
            current: self.tail,
            list: self,
        }
    }

    /// Return an iterator that moves from front to back
    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            current: self.head,
            marker: PhantomData,
        }
    }
}

// the cursor is expected to act as if it is at the position of an element
// and it also has to work with and be able to insert into an empty list.
impl<T> Cursor<'_, T> {
    /// Take a mutable reference to the current element
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            None
        } else {
            // Safety: self.current is a valid pointer to a Node<T> owned by the list.
            // The list is held by &mut self.list, ensuring exclusive access.
            unsafe { Some(&mut (*self.current).data) }
        }
    }

    /// Move one position forward (towards the back) and
    /// return a reference to the new position
    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            None
        } else {
            // Safety: self.current is a valid pointer to a Node<T> owned by the list.
            self.current = unsafe { (*self.current).next };
            if self.current.is_null() {
                None
            } else {
                // Safety: self.current is a valid pointer to a Node<T> owned by the list.
                unsafe { Some(&mut (*self.current).data) }
            }
        }
    }

    /// Move one position backward (towards the front) and
    /// return a reference to the new position
    pub fn prev(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            None
        } else {
            // Safety: self.current is a valid pointer to a Node<T> owned by the list.
            self.current = unsafe { (*self.current).prev };
            if self.current.is_null() {
                None
            } else {
                // Safety: self.current is a valid pointer to a Node<T> owned by the list.
                unsafe { Some(&mut (*self.current).data) }
            }
        }
    }

    /// Remove and return the element at the current position and move the cursor
    /// to the neighboring element that's closest to the back. This can be
    /// either the next or previous position.
    pub fn take(&mut self) -> Option<T> {
        if self.current.is_null() {
            return None;
        }

        let current = self.current;
        // Safety: current is a valid pointer to a Node<T> owned by the list.
        let prev = unsafe { (*current).prev };
        let next = unsafe { (*current).next };

        // Update neighbors
        if prev.is_null() {
            // Current is head
            self.list.head = next;
        } else {
            // Safety: prev is a valid node pointer
            unsafe { (*prev).next = next; }
        }

        if next.is_null() {
            // Current is tail
            self.list.tail = prev;
        } else {
            // Safety: next is a valid node pointer
            unsafe { (*next).prev = prev; }
        }

        // Move cursor to next (closest to back), or prev if next is null
        self.current = if next.is_null() { prev } else { next };

        self.list.len -= 1;

        // Safety: current is a valid node pointer owned by the list
        let node = unsafe { Box::from_raw(current) };
        Some(node.data)
    }

    pub fn insert_after(&mut self, element: T) {
        let new_node = Box::into_raw(Box::new(Node {
            data: element,
            prev: ptr::null_mut(),
            next: ptr::null_mut(),
        }));

        if self.current.is_null() {
            // List is empty or cursor is at a sentinel position (though typically cursor is on a node)
            // If list is empty, insert as head and tail
            if self.list.head.is_null() {
                self.list.head = new_node;
                self.list.tail = new_node;
                self.current = new_node;
            } else {
                // This case shouldn't happen if cursor is always on a valid node or null for empty list
                // But if cursor is null and list is not empty, it's ambiguous.
                // Let's assume if current is null, we append to tail? Or prepend?
                // The prompt says "work with and be able to insert into an empty list".
                // If current is null, let's treat it as inserting at the end? Or beginning?
                // Usually cursor_front/back on empty list returns cursor with current=null.
                // Let's insert at the end if current is null.
                unsafe {
                    (*self.list.tail).next = new_node;
                    (*new_node).prev = self.list.tail;
                    self.list.tail = new_node;
                    self.current = new_node;
                }
            }
        } else {
            // Insert after current
            // Safety: self.current is valid
            let next = unsafe { (*self.current).next };
            
            // Safety: self.current is valid
            unsafe {
                (*self.current).next = new_node;
                (*new_node).prev = self.current;
            }

            if next.is_null() {
                // Current was tail
                self.list.tail = new_node;
            } else {
                // Safety: next is valid
                unsafe {
                    (*next).prev = new_node;
                    (*new_node).next = next;
                }
            }
        }
        
        self.list.len += 1;
    }

    pub fn insert_before(&mut self, element: T) {
        let new_node = Box::into_raw(Box::new(Node {
            data: element,
            prev: ptr::null_mut(),
            next: ptr::null_mut(),
        }));

        if self.current.is_null() {
            // List is empty or cursor is null
            if self.list.head.is_null() {
                self.list.head = new_node;
                self.list.tail = new_node;
                self.current = new_node;
            } else {
                // If current is null but list is not empty, insert at head?
                // Let's insert at head.
                unsafe {
                    (*self.list.head).prev = new_node;
                    (*new_node).next = self.list.head;
                    self.list.head = new_node;
                    self.current = new_node;
                }
            }
        } else {
            // Insert before current
            // Safety: self.current is valid
            let prev = unsafe { (*self.current).prev };

            // Safety: self.current is valid
            unsafe {
                (*self.current).prev = new_node;
                (*new_node).next = self.current;
            }

            if prev.is_null() {
                // Current was head
                self.list.head = new_node;
            } else {
                // Safety: prev is valid
                unsafe {
                    (*prev).next = new_node;
                    (*new_node).prev = prev;
                }
            }
        }

        self.list.len += 1;
    }
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<&'a T> {
        if self.current.is_null() {
            None
        } else {
            // Safety: self.current is a valid pointer to a Node<T> owned by the list.
            // The list is immutable during iteration.
            let data = unsafe { &(*self.current).data };
            self.current = unsafe { (*self.current).next };
            Some(data)
        }
    }
}

impl<T> Drop for LinkedList<T> {
    fn drop(&mut self) {
        let mut current = self.head;
        while !current.is_null() {
            let next = unsafe { (*current).next };
            unsafe {
                let _ = Box::from_raw(current);
            }
            current = next;
        }
    }
}

// Safety: LinkedList<T> is Send if T is Send, because the nodes are allocated on the heap
// and can be moved between threads. The raw pointers are managed correctly.
unsafe impl<T: Send> Send for LinkedList<T> {}

// Safety: LinkedList<T> is Sync if T is Sync, because the internal structure
// (pointers and length) can be shared across threads if T can be shared.
// Note: This assumes that concurrent access is managed by the caller (e.g., via Mutex)
// or that the list is only accessed immutably via Sync. Since our methods take &mut self
// for mutation, Sync allows &LinkedList to be shared.
unsafe impl<T: Sync> Sync for LinkedList<T> {}