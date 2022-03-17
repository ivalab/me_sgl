(define (domain cook)
    (:predicates (GRASPABLE ?x)
    			 (SLICED ?x)
				 (SLICE_CONTAINABLE ?x)
    			 (TOGGLEABLE ?x)
    			 (CONTAINABLE ?x)
    			 (OPENABLE ?x) 
				 (CLOSEABLE ?x) 
				 (OPENED ?x)
				 (CLOSED ?x)
                 (carry ?x ?y)
				 (free ?x)                 
				 (contains ?x ?y)
				 (cook ?x ?y))

    (:action pickup :parameters(?x ?y)
        :precondition (and (GRASPABLE ?x)
	                   (free ?y))			   
        :effect       (and (carry ?y ?x)
	                   (not (free ?y))
	                   (not (GRASPABLE ?x))))

	(:action open :parameters(?x ?y)
        :precondition (and (OPENABLE ?x)
	                   (free ?y))			   
        :effect       (and (OPENED ?x)
						   (not (CLOSED ?x))))

    (:action dropoff :parameters (?x ?y ?z)
        :precondition (and (carry ?y ?x) (or 
											(and (SLICE_CONTAINABLE ?z) (SLICED ?x))
											(and (CONTAINABLE ?z) (OPENED ?z))))			   
	:effect       (and (contains ?x ?z)
	                   (free ?y)
			   		   (not (carry ?y ?x))))

	(:action close :parameters(?x ?y)
        :precondition (and (CLOSEABLE ?x) (OPENED ?x)
	                   (free ?y))			   
        :effect       (and (CLOSED ?x) (not (OPENED ?x))))

	(:action toggle :parameters (?x ?y)
        :precondition (and (contains ?x ?y) (TOGGLEABLE ?y) (or 
																(and (CONTAINABLE ?y) (CLOSED ?y))
																(and (SLICE_CONTAINABLE ?y))))			   
	:effect       (and (cook ?x ?y)))

)
	     
