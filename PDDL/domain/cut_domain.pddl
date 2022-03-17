(define (domain cut)
    (:predicates (carry ?x ?y)
                 (cut ?x ?y)
		 		 (free ?x)
                 (CUTTABLE ?x)
                 (CUTTOOL ?x))

    (:action pickup :parameters(?x ?y)
        :precondition (and (CUTTOOL ?x)
	                   (free ?y))
			   
        :effect       (and (carry ?y ?x)
	                   (not (free ?y))))

    (:action cut :parameters (?z ?x ?y)
        :precondition (and (carry ?y ?x)
	                   (CUTTABLE ?z))
			   
	:effect       (and (cut ?z ?x)))

)
	     
