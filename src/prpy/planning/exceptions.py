
class PlanningError(Exception):
    pass


class UnsupportedPlanningError(PlanningError):
    pass


class ConstraintViolationPlanningError(PlanningError):
    def __init__(self, 
                constraint_name, 
                threshold = None,
                violation_by = None, 
                base_message='Violates constraint'):
        self.constraint_name = constraint_name 
        self.threshold = threshold
        self.violation_by = violation_by

        super(ConstraintViolationPlanningError, self).__init__(
            '{:s}: {:s}'.format(
                base_message,
                self.constraint_name
            )
        )

    pass


class CollisionPlanningError(PlanningError):
    def __init__(self, link1, link2, base_message='Detected collision'):
        self.link1 = link1
        self.link2 = link2

        super(CollisionPlanningError, self).__init__(
            '{:s}: {:s} x {:s}.'.format(
                base_message,
                self._get_link_str(link1),
                self._get_link_str(link2)
            )
        )

    @classmethod
    def FromReport(cls, report):
        return cls(report.plink1, report.plink2)

    @staticmethod
    def _get_link_str(link):
        if link is not None:
            return '<{:s}, {:s}>'.format(
                link.GetParent().GetName(), link.GetName())
        else:
            return '<unknown>'


class JointLimitError(PlanningError):
    def __init__(self, robot, dof_index, dof_value, dof_limit, description):
        self.robot = robot
        self.dof_index = dof_index
        self.dof_value = dof_value
        self.dof_limit = dof_limit

        joint = robot.GetJointFromDOFIndex(dof_index)
        if dof_value < dof_limit:
            direction = 'lower'
            comparison = '<'
        else:
            direction = 'upper'
            comparison = '>'

        super(JointLimitError, self).__init__(
            'Robot "{robot_name:s}" joint "{joint_name:s} axis {joint_axis:d}'
            ' violates {direction:s} {description:s} limit:'
            ' {dof_value:.5f} {comparison:s} {dof_limit:.5f}'.format(
                robot_name=robot.GetName(),
                joint_name=joint.GetName(),
                joint_axis=dof_index - joint.GetDOFIndex(),
                dof_value=dof_value,
                dof_limit=dof_limit,
                comparison=comparison,
                direction=direction,
                description=description))


class SelfCollisionPlanningError(CollisionPlanningError):
    pass


class TimeoutPlanningError(PlanningError):
    def __init__(self, timelimit=None):
        if timelimit is not None:
            message = 'Exceeded {:.3f} s time limit.'.format(timelimit)
        else:
            message = 'Exceeded time limit.'

        super(TimeoutPlanningError, self).__init__(message)


class MetaPlanningError(PlanningError):
    """
    A metaplanning error indicates that a planning operation that calls one or
    more other planners internally failed due to the internal planning calls
    failing.
    """
    def __init__(self, message, errors):
        PlanningError.__init__(self, message)
        self.errors = errors

    # TODO: Print the inner exceptions.


class ClonedPlanningError(PlanningError):
    """
    A cloned planning error indicates that planning failed because a
    ClonedPlanningMethod was unable to clone the environment successfully.

    This most commonly occurs when a planner attempts to clone while in
    collision, which can corrupt the environment before the planner would
    have a chance to detect the collision.
    """
    def __init__(self, cloning_error):
        super(ClonedPlanningError, self).__init__(
            "Failed to clone: {:s}".format(cloning_error))
        self.error = cloning_error
