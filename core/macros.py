# work_type
UPLOAD = "upload"
PROCESS = "process"
UPLOAD_AND_PROCESS = "upload_process"
OTHER = "other"

# status
IN_PROGRESS = "in progress"
TAGS_READY = "tags ready"
COMPLETE = "complete"
FAILED = "failed"
ABORTED = "aborted"

# stage
S_START = "start"
S_UPLOAD_AND_PROCESS = "upload and process"
S_POST_PROCESS = "post-process"
S_FINISH = "finish"

# incompatible work type
INCOMPATIBLE_WORK_TYPE = [UPLOAD_AND_PROCESS, UPLOAD, PROCESS]

# statuses - end polling
END_POLLING_STATUS = [COMPLETE, FAILED, ABORTED, TAGS_READY]

# statuses - can abort
CAN_ABORT_STATUS = [IN_PROGRESS, TAGS_READY]
