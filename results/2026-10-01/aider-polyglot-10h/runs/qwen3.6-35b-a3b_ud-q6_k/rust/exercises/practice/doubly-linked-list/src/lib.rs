// this module adds some functionality based on the required implementations
// here like: `LinkedList::pop_back` or `Clone for LinkedList<T>`
// You are free to use anything in it, but it's mainly for the test framework.
mod pre_implemented;

use std::ptr::NonNull;

pub struct LinkedList<T> {
    head: Option<NonNull<Node<T>>>,
    tail: Option<NonNull<Node<T>>>,
    len: usize,
}

struct Node<T> {
    data: T,
    prev: Option<NonNull<Node<T>>>,
    next: Option<NonNull<Node<T>>>,
}

pub struct Cursor<'a, T> {
    list: &'a mut LinkedList<T>,
    ptr: Option<NonNull<Node<T>>>,
}

pub struct Iter<'a, T> {
    current: Option<NonNull<Node<T>>>,
    _marker: std::marker::PhantomData<&'a T>,
}

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList {
            head: None,
            tail: None,
            len: 0,
        }
    }

    // You may be wondering why it's necessary to have is_empty()
    // when it can easily be determined from len().
    // It's good custom to have both because len() can be expensive for some types,
    // whereas is_empty() is almost always cheap.
    // (Also ask yourself whether len() is expensive for LinkedList)
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn len(&self) -> usize {
        self.len
    }

    /// Return a cursor positioned on the front element
    pub fn cursor_front(&mut self) -> Cursor<'_, T> {
        let ptr = self.head;
        Cursor {
            list: self,
            ptr,
        }
    }

    /// Return a cursor positioned on the back element
    pub fn cursor_back(&mut self) -> Cursor<'_, T> {
        let ptr = self.tail;
        Cursor {
            list: self,
            ptr,
        }
    }

    /// Return an iterator that moves from front to back
    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            current: self.head,
            _marker: std::marker::PhantomData,
        }
    }
}

// the cursor is expected to act as if it is at the position of an element
// and it also has to work with and be able to insert into an empty list.
impl<T> Cursor<'_, T> {
    /// Take a mutable reference to the current element
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        self.ptr.map(|mut ptr| unsafe { &mut ptr.as_mut().data })
    }

    /// Move one position forward (towards the back) and
    /// return a reference to the new position
    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<&mut T> {
        self.ptr = self.ptr.and_then(|ptr| unsafe { ptr.as_ref().next });
        self.peek_mut()
    }

    /// Move one position backward (towards the front) and
    /// return a reference to the new position
    pub fn prev(&mut self) -> Option<&mut T> {
        self.ptr = self.ptr.and_then(|ptr| unsafe { ptr.as_ref().prev });
        self.peek_mut()
    }

    /// Remove and return the element at the current position and move the cursor
    /// to the neighboring element that's closest to the back. This can be
    /// either the next or previous position.
    pub fn take(&mut self) -> Option<T> {
        let ptr = self.ptr?;
        unsafe {
            let mut ptr = ptr;
            let node = ptr.as_mut();
            let prev = node.prev;
            let next = node.next;

            // Update neighbors
            if let Some(mut prev_ptr) = prev {
                prev_ptr.as_mut().next = next;
            } else {
                // This was the head
                self.list.head = next;
            }

            if let Some(mut next_ptr) = next {
                next_ptr.as_mut().prev = prev;
            } else {
                // This was the tail
                self.list.tail = prev;
            }

            // Clear current node pointers to avoid dangling references
            node.prev = None;
            node.next = None;
            
            self.list.len -= 1;

            // Move cursor to next if it exists, otherwise prev
            self.ptr = next.or(prev);

            // Extract data
            Some(std::ptr::read(&node.data))
        }
    }

    pub fn insert_after(&mut self, element: T) {
        unsafe {
            let new_node = NonNull::new_unchecked(Box::into_raw(Box::new(Node {
                data: element,
                prev: self.ptr,
                next: None,
            })));

            if let Some(mut current_ptr) = self.ptr {
                let current = current_ptr.as_mut();
                let old_next = current.next;
                
                current.next = Some(new_node);
                
                if let Some(mut old_next_ptr) = old_next {
                    old_next_ptr.as_mut().prev = Some(new_node);
                } else {
                    // Inserted at tail
                    self.list.tail = Some(new_node);
                }
            } else {
                // List was empty
                self.list.head = Some(new_node);
                self.list.tail = Some(new_node);
            }
            
            self.list.len += 1;
            self.ptr = Some(new_node);
        }
    }

    pub fn insert_before(&mut self, element: T) {
        unsafe {
            let new_node = NonNull::new_unchecked(Box::into_raw(Box::new(Node {
                data: element,
                prev: None,
                next: self.ptr,
            })));

            if let Some(mut current_ptr) = self.ptr {
                let current = current_ptr.as_mut();
                let old_prev = current.prev;
                
                current.prev = Some(new_node);
                
                if let Some(mut old_prev_ptr) = old_prev {
                    old_prev_ptr.as_mut().next = Some(new_node);
                } else {
                    // Inserted at head
                    self.list.head = Some(new_node);
                }
            } else {
                // List was empty
                self.list.head = Some(new_node);
                self.list.tail = Some(new_node);
            }
            
            self.list.len += 1;
            self.ptr = Some(new_node);
        }
    }
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<&'a T> {
        self.current.map(|ptr| {
            let node = unsafe { ptr.as_ref() };
            self.current = node.next;
            &node.data
        })
    }
}

impl<T> Drop for LinkedList<T> {
    fn drop(&mut self) {
        let mut current = self.head;
        while let Some(mut ptr) = current {
            unsafe {
                let node = ptr.as_mut();
                current = node.next;
                drop(Box::from_raw(ptr.as_ptr()));
            }
        }
        self.head = None;
        self.tail = None;
        self.len = 0;
    }
}

// Safety: LinkedList only contains raw pointers to T.
// If T is Send, then the data inside the nodes is Send.
// The list structure itself (pointers, len) is just integers/pointers which are Send.
// We can safely send the list to another thread.
unsafe impl<T: Send> Send for LinkedList<T> {}

// Safety: LinkedList only contains raw pointers to T.
// If T is Sync, then the data inside the nodes is Sync.
// We can safely share references to the list across threads.
// Note: The list itself is not thread-safe for concurrent mutation without external synchronization,
// but the type system allows sharing the LinkedList<T> if T is Sync.
unsafe impl<T: Sync> Sync for LinkedList<T> {}
