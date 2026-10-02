// this module adds some functionality based on the required implementations
// here like: `LinkedList::pop_back` or `Clone for LinkedList<T>`
// You are free to use anything in it, but it's mainly for the test framework.
mod pre_implemented;

use std::marker::PhantomData;
use std::ptr;

struct Node<T> {
    elem: T,
    next: *mut Node<T>,
    prev: *mut Node<T>,
}

impl<T> Node<T> {
    unsafe fn new(elem: T) -> *mut Node<T> {
        Box::into_raw(Box::new(Node {
            elem,
            next: ptr::null_mut(),
            prev: ptr::null_mut(),
        }))
    }
}

pub struct LinkedList<T> {
    head: *mut Node<T>,
    len: usize,
    _marker: PhantomData<T>,
}

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList {
            head: ptr::null_mut(),
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
        let head = self.head;
        Cursor {
            list: self,
            current: head,
        }
    }

    /// Return a cursor positioned on the back element
    pub fn cursor_back(&mut self) -> Cursor<'_, T> {
        let head = self.head;
        if head.is_null() {
            return Cursor {
                list: self,
                current: ptr::null_mut(),
            };
        }
        
        // Traverse to the end
        let mut current = head;
        unsafe {
            while (*current).next != ptr::null_mut() {
                current = (*current).next;
            }
        }
        Cursor {
            list: self,
            current,
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

impl<T> Drop for LinkedList<T> {
    fn drop(&mut self) {
        let mut current = self.head;
        while !current.is_null() {
            let next = unsafe { (*current).next };
            unsafe {
                drop(Box::from_raw(current));
            }
            current = next;
        }
    }
}

// Safety: LinkedList is Send if T is Send, because it owns its data exclusively.
unsafe impl<T: Send> Send for LinkedList<T> {}
// Safety: LinkedList is Sync if T is Sync, because shared references only allow reading,
// and the internal pointers are not exposed in a way that allows data races on the structure itself
// when accessed via &self (iter only).
unsafe impl<T: Sync> Sync for LinkedList<T> {}

pub struct Cursor<'a, T> {
    list: &'a mut LinkedList<T>,
    current: *mut Node<T>,
}

impl<T> Cursor<'_, T> {
    /// Take a mutable reference to the current element
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            None
        } else {
            // Safety: self.current is a valid pointer to a node owned by self.list.
            // We have exclusive access to self.list via &mut self.
            Some(unsafe { &mut (*self.current).elem })
        }
    }

    /// Move one position forward (towards the back) and
    /// return a reference to the new position
    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            return None;
        }
        
        let next_ptr = unsafe { (*self.current).next };
        if next_ptr.is_null() {
            None
        } else {
            self.current = next_ptr;
            // Safety: self.current is now a valid pointer to a node owned by self.list.
            Some(unsafe { &mut (*self.current).elem })
        }
    }

    /// Move one position backward (towards the front) and
    /// return a reference to the new position
    pub fn prev(&mut self) -> Option<&mut T> {
        if self.current.is_null() {
            return None;
        }
        
        let prev_ptr = unsafe { (*self.current).prev };
        if prev_ptr.is_null() {
            None
        } else {
            self.current = prev_ptr;
            // Safety: self.current is now a valid pointer to a node owned by self.list.
            Some(unsafe { &mut (*self.current).elem })
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
        let prev = unsafe { (*current).prev };
        let next = unsafe { (*current).next };

        // Update neighbors
        unsafe {
            if !prev.is_null() {
                (*prev).next = next;
            } else {
                // current was head
                self.list.head = next;
            }
            
            if !next.is_null() {
                (*next).prev = prev;
            }
        }

        self.list.len -= 1;

        // Move cursor to next if available, else prev
        if !next.is_null() {
            self.current = next;
        } else {
            self.current = prev;
        }

        // Safety: We are removing the node from the list. We take ownership of the element.
        // We must drop the node itself.
        let elem = unsafe { ptr::read(&mut (*current).elem) };
        unsafe {
            drop(Box::from_raw(current));
        }
        
        Some(elem)
    }

    pub fn insert_after(&mut self, element: T) {
        let new_node = unsafe { Node::new(element) };
        
        if self.current.is_null() {
            // List is empty, insert as head
            self.list.head = new_node;
            self.current = new_node;
        } else {
            let current = self.current;
            let next = unsafe { (*current).next };
            
            unsafe {
                (*new_node).next = next;
                (*new_node).prev = current;
                (*current).next = new_node;
                
                if !next.is_null() {
                    (*next).prev = new_node;
                }
            }
            
            self.current = new_node;
        }
        
        self.list.len += 1;
    }

    pub fn insert_before(&mut self, element: T) {
        let new_node = unsafe { Node::new(element) };
        
        if self.current.is_null() {
            // List is empty, insert as head
            self.list.head = new_node;
            self.current = new_node;
        } else {
            let current = self.current;
            let prev = unsafe { (*current).prev };
            
            unsafe {
                (*new_node).next = current;
                (*new_node).prev = prev;
                (*current).prev = new_node;
                
                if !prev.is_null() {
                    (*prev).next = new_node;
                } else {
                    // current was head
                    self.list.head = new_node;
                }
            }
            
            self.current = new_node;
        }
        
        self.list.len += 1;
    }
}

pub struct Iter<'a, T> {
    current: *const Node<T>,
    _marker: PhantomData<&'a T>,
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<&'a T> {
        if self.current.is_null() {
            return None;
        }
        
        // Safety: self.current is a valid pointer to a node in the list.
        // We are only reading, and the list is not being mutated during iteration.
        let elem = unsafe { &(*self.current).elem };
        self.current = unsafe { (*self.current).next as *const Node<T> };
        
        Some(elem)
    }
}
