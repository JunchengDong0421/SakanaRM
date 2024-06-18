# work_type
UPLOAD = 0
PROCESS = 1
OTHER = 2

# status
PENDING = 0
COMPLETED = 1
FAILED = 2
ABORTED = 3

# stage
S_START = 0
S_UPLOADING = 1
S_PROCESSING_0 = 2
S_PROCESSING_1 = 3
S_PROCESSING_2 = 4
S_END = 5

# incompatible work type
INCOMPATIBLE_WORK_TYPE = [UPLOAD, PROCESS]

# statuses - end polling
END_POLLING_STATUS = [COMPLETED, FAILED, ABORTED]

# statuses - can abort
CAN_ABORT_STATUS = [PENDING]

# statuses - can archive
CAN_ARCHIVE_STATUS = [COMPLETED, FAILED, ABORTED]

# threshold of the number of pending workflows
PENDING_WORKFLOWS_LIMIT = 5
