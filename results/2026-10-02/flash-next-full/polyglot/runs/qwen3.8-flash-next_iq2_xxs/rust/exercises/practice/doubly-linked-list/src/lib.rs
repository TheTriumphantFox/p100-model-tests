// this module adds some functionality based on the required implementations
// here like: `LinkedList::pop_back` or `Clone for LinkedList<T>`
// You are free to use anything in it, but it's mainly for the test framework.
mod pre_implemented;

use std::marker::PhantomData;
use std::ptr::NonNull;

// The node structure for the doubly linked list
// We use Option<NonNull> to allow for null pointers (end of list)
#[derive(Debug)]
struct Node<T> {
    pub prev: Option<NonNull<Node<T>>>,
    pub data: T,
    pub next: Option<NonNull<Node<T>>>,
}

// The LinkedList struct holds the head and tail pointers
// PhantomData is used to ensure covariance over T, as raw pointers are invariant
pub struct LinkedList<T> {
    pub head: Option<NonNull<Node<T>>>,
    pub tail: Option<NonNull<Node<T>>>,
    pub len: usize,
}

// The Cursor holds a pointer to the current node
pub struct Cursor<'a, T> {
    pub cursor: Option<NonNull<Node<T>>>,
    pub list: &'a mut LinkedList<T>,
}

// The Iter holds a pointer to the current node in the iteration
pub struct Iter<'a, T> {
    pub front: Option<NonNull<Node<T>>>,
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
        Cursor {
            cursor: self.head,
            list: self,
        }
    }

    /// Return a cursor positioned on the back element
    pub fn cursor_back(&mut self) -> Cursor<'_, T> {
        Cursor {
            cursor: self.tail,
            list: self,
        }
    }

    /// Return an iterator that moves from front to back
    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            front: self.head,
        }
    }

    /// Insert a new node with the given data after the current cursor position
    pub fn insert_after(&mut self, data: T) {
        let new_node = Box::new(Node {
            prev: None,
            data,
            next: None,
        });
        let new_node = unsafe { NonNull::new_unchecked(Box::into_raw(Box::new(new_node))) };

        if let Some(current_node) = self.cursor {
            unsafe {
                let current_node = current_node.as_ref();
                let next = current_node.next;

                // Set new node's pointers
                new_node.as_ref().prev = Some(current_node);
                new_node.as_ref().next = next;

                // Update current node's next
                let mut current_node_ptr = self.cursor.unwrap();
                current_node_ptr.as_mut().next = Some(new_node);

                // Update next node's prev
                if let Some(mut next_node) = next {
                    next_node.as_mut().prev = Some(new_node);
                } else {
                    self.list.tail = Some(new_node);
                }

                self.list.len += 1;
            }
        } else {
            // List was empty or cursor was None, insert as first element
            unsafe {
                new_node.as_ref().prev = None;
                new_node.as_ref().next = None;
                self.list.head = Some(new_node);
                self.list.tail = Some(new_node);
                self.list.len += 1;
            }
        }
        self.cursor = Some(new_node);
    }

    /// Insert a new node with the given data before the current cursor position
    pub fn insert_before(&mut self, data: T) {
        let new_node = Box::new(Node {
            prev: None,
            data,
            next: None,
        });
        let new_node = unsafe { NonNull::new_unchecked(Box::into_raw(Box::new(new_node))) };

        if let Some(current_node) = self.cursor {
            unsafe {
                let current_node = current_node.as_ref();
                let prev = current_node.prev;

                // Set new node's pointers
                new_node.as_ref().prev = prev;
                new_node.as_ref().next = Some(current_node);

                // Update current node's prev
                let mut current_node_ptr = self.cursor.unwrap();
                current_node_ptr.as_mut().prev = Some(new_node);

                // Update prev node's next
                if let Some(mut prev_node) = prev {
                    prev_node.as_mut().next = Some(new_node);
                } else {
                    self.list.head = Some(new_node);
                }

                self.list.len += 1;
            }
        } else {
            // List was empty or cursor was None, insert as first element
            unsafe {
                new_node.as_ref().prev = None;
                new_node.as_ref().next = None;
                self.list.head = Some(new_node);
                self.list.tail = Some(new_node);
                self.list.len += 1;
            }
        }
        self.cursor = Some(new_node);
    }

    /// Remove the element at the current cursor position and move the cursor
    /// to the neighboring element that's closest to the back. This can be
    /// either the next or previous position.
    pub fn take(&mut self) -> Option<T> {
        if let Some(current_node) = self.cursor {
            unsafe {
                let current_node = current_node.as_ref();
                let prev = current_node.prev;
                let next = current_node.next;

                // Update neighbors
                if let Some(mut prev_node) = prev {
                    prev_node.as_mut().next = next;
                } else {
                    self.list.head = next;
                }

                if let Some(mut next_node) = next {
                    next_node.as_mut().prev = prev;
                } else {
                    self.list.tail = prev;
                }

                self.list.len -= 1;

                // Move cursor to the next element (closest to back)
                self.cursor = next;

                // Return the data
                let data = std::ptr::read(&current_node.data);
                
                // Drop the node itself (excluding the data which we moved out)
                // We must drop the node structure itself. 
                // Since we moved out data, we drop the rest of the node.
                // Actually, we just need to deallocate the node.
                // We can drop the node by dropping the Box that owns it.
                // But we are using raw pointers. We need to manually drop the node.
                // We can drop the node by calling drop on the pointer, but we moved out data.
                // Let's just drop the node.
                // Wait, if we drop the node, we drop the data too? No, we moved it out.
                // We need to drop the node's memory.
                // We can do: drop(Box::from_raw(current_node as *const _ as *mut Node<T>));
                // But we moved out data. So we shouldn't drop data.
                // Let's just drop the node.
                // Actually, simply dropping the node is fine if we moved out data?
                // No, dropping the node drops the data field.
                // We moved out the data. So we shouldn't drop it.
                // We can use ManuallyDrop or just drop the node.
                // Let's just drop the node.
                // Actually, we can just drop the node.