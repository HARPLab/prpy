#!/usr/bin/env python

# Copyright (c) 2013, Carnegie Mellon University
# All rights reserved.
# Authors: Michael Koval <mkoval@cs.cmu.edu>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of Carnegie Mellon University nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging, numpy, openravepy, os, tempfile
from base import BasePlanner, PlanningError, UnsupportedPlanningError, PlanningMethod

class OMPLPlanner(BasePlanner):
    def __init__(self, algorithm='RRTConnect'):
        self.env = openravepy.Environment()
        self.algorithm = algorithm
        try:
            self.planner = openravepy.RaveCreatePlanner(self.env, 'OMPL')
        except openravepy.openrave_exception:
            raise UnsupportedPlanningError('Unable to create OMPL module.')

    def __str__(self):
        return 'OMPL {0:s}'.format(self.algorithm)

    @PlanningMethod
    def PlanToConfiguration(self, robot, goal, **kw_args):
        params = openravepy.Planner.PlannerParameters()
        params.SetRobotActiveJoints(robot)
        params.SetGoalConfig(goal)

        traj = openravepy.RaveCreateTrajectory(self.env, '')

        with self.env:
            try:
                self.planner.InitPlan(robot, params)
                status = self.planner.PlanPath(traj, releasegil=True)
            except Exception as e:
                raise PlanningError('Planning failed with error: {0:s}'.format(e))

        from openravepy import PlannerStatus
        if status not in [ PlannerStatus.HasSolution, PlannerStatus.InterruptedWithSolution ]:
            raise PlanningError('Planner returned with status {0:s}.'.format(str(status)))

        return traj
