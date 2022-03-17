(define (domain delivery)
    (:predicates (GRASPABLE ?x)
				 (CONTAINABLE ?X)
                 (carry ?x ?y)
		 		 (free ?x)
		 		 (contain ?x ?y))

    (:action pickup :parameters(?x ?y)
        :precondition (and (GRASPABLE ?x)
	                   (free ?y))
			   
        :effect       (and (carry ?y ?x)
	                   (not (free ?y))
	                   (not (GRASPABLE ?x))))

    (:action delivery :parameters (?x ?y ?z)
        :precondition (and (carry ?y ?x)
	                   (CONTAINABLE ?z))
			   
	:effect       (and (contain ?x ?z) 
					   (free ?y)
			   		   (not (carry ?y ?x))))

)
	     
