(define (domain clean)
    (:predicates (GRASPABLE ?x)
                 (carry ?x ?y)
		 		 (free ?x)
                 (CONTAINABLE ?x)
                 (TOGGLEABLE ?x)
				 (contains ?x ?y)
				 (clean ?x ?y))

    (:action pickup :parameters(?x ?y)
        :precondition (and (GRASPABLE ?x)
	                   (free ?y))
			   
        :effect       (and (carry ?y ?x)
	                   (not (free ?y))
	                   (not (GRASPABLE ?x))))

    (:action dropoff :parameters (?x ?y ?z)
        :precondition (and (carry ?y ?x)
	                   (CONTAINABLE ?z))
			   
	:effect       (and (contains ?x ?z)
                       (GRASPABLE ?x)
	                   (free ?y)
			   		   (not (carry ?y ?x))))

	(:action toggle :parameters (?x ?y ?z)
        :precondition (and (contains ?x ?y) (TOGGLEABLE ?z))
			   
	:effect       (and (clean ?x ?y)))

)
	     
