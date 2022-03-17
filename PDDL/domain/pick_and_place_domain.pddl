(define (domain pick_and_place)
    (:predicates (GRASPABLE ?x)
    			 (CONTAINABLE ?x)
                 (carry ?x ?y)
                 (contain ?x ?y)
		 		 (free ?x))

    (:action pickup :parameters(?x ?y)
        :precondition (and (GRASPABLE ?x)
	                   (free ?y))
			   
        :effect       (and (carry ?y ?x)
	                   (not (free ?y))
	                   (not (GRASPABLE ?x))))

    (:action place :parameters (?x ?y ?z)
        :precondition (and (carry ?y ?x) (CONTAINABLE ?z))
			   
	:effect       (and (GRASPABLE ?x)
	                   (free ?y)
			   		   (not (carry ?y ?x))
			   		   (contain ?x ?z)))

)
	     
